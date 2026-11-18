import logging
import os
from urllib.parse import urlsplit
from office365.sharepoint.client_context import ClientContext
from office365.runtime.client_request_exception import ClientRequestException

logger = logging.getLogger(__name__)

# SharePoint configuration
inventory_list_name = 'Inventory'

class SharePointConfigurationError(ValueError):
    """The app has no usable SharePoint site configured."""


def connect_sharepoint():
    site = os.environ.get("SHAREPOINT_SITE_URL", "").strip()
    tenant = os.environ.get("SHAREPOINT_TENANT_ID", "").strip()
    client_id = os.environ.get("SHAREPOINT_CLIENT_ID", "").strip()
    parsed = urlsplit(site)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise SharePointConfigurationError("Set SHAREPOINT_SITE_URL to your organization's HTTPS SharePoint site.")
    if not tenant or not client_id:
        raise SharePointConfigurationError("Set SHAREPOINT_TENANT_ID and SHAREPOINT_CLIENT_ID for the registered desktop app.")
    try:
        ctx = ClientContext(site).with_interactive(tenant, client_id)
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        return ctx
    except ClientRequestException as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        logger.warning("SharePoint sign-in failed (HTTP %s)", status or "unknown")
        raise ValueError("SharePoint could not complete sign-in. Check the site configuration and account access.") from None
    except Exception as exc:
        logger.error("SharePoint connection failed (%s)", type(exc).__name__)
        raise ValueError("The app could not connect to SharePoint. Check the site configuration and network connection.") from None


def get_sharepoint_list_items(ctx, list_name, page_size=100, page_number=1, field=None, value=None):
    try:
        target_list = ctx.web.lists.get_by_title(list_name)
        items_query = target_list.items

        if field and value:
            field_mappings = {
                "Item": "Title",
                "Description": "field_1",
                "S/N": "field_2",
                "Location": "field_3",
                "Condition": "Condition",
                "Assigned To": "AssignedTo",
                "Date": "field_4",
                "Cost": "field_5",
                "Funding": "field_6",
                "Status": "field_7"
            }
            internal_field_name = field_mappings.get(field, field)
            items_query = items_query.filter(f"substringof('{value}', {internal_field_name})")

        all_items = items_query.get_all().execute_query()

        total_items_count = len(all_items)
        total_pages = (total_items_count + page_size - 1) // page_size

        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        paged_items = all_items[start_index:end_index]

        field_mappings = {
            "Title": "Item",
            "field_1": "Description",
            "field_2": "S/N",
            "field_3": "Location",
            "Condition": "Condition",
            "AssignedTo": "Assigned To",
            "field_4": "Date",
            "field_5": "Cost",
            "field_6": "Funding",
            "field_7": "Status"
        }

        mapped_items = []
        for item in paged_items:
            mapped_item = {"ID": item.properties.get('ID', ''), "Item ID": item.properties.get('ID', '')}
            for internal_name, display_name in field_mappings.items():
                mapped_item[display_name] = item.properties.get(internal_name, '')
            mapped_items.append(mapped_item)

        return mapped_items, page_number < total_pages, page_number, total_pages

    except Exception as e:
        logger.error("SharePoint operation get_sharepoint_list_items failed (%s)", type(e).__name__)
        raise

def get_sharepoint_item(ctx, list_name, item_id):
    try:
        target_list = ctx.web.lists.get_by_title(list_name)
        
        item = target_list.items.get_by_id(item_id).get().execute_query()

        field_mappings = {
            "Title": "Item",
            "field_1": "Description",
            "field_2": "S/N",
            "field_3": "Location",
            "Condition": "Condition",
            "AssignedTo": "Assigned To",
            "field_4": "Date",
            "field_5": "Cost",
            "field_6": "Funding",
            "field_7": "Status"
        }

        mapped_item = {}
        for internal_name, display_name in field_mappings.items():
            mapped_item[display_name] = item.properties.get(internal_name, '')

        return mapped_item
    except Exception as e:
        logger.error("SharePoint operation get_sharepoint_item failed (%s)", type(e).__name__)
        raise

def update_sharepoint_item(ctx, list_name, item_id, updated_properties):
    try:
        target_list = ctx.web.lists.get_by_title(list_name)
        item = target_list.items.get_by_id(item_id)

        field_mappings = {
            "Item": "Title",
            "Description": "field_1",
            "S/N": "field_2",
            "Location": "field_3",
            "Condition": "Condition",
            "Assigned To": "AssignedTo",
            "Date": "field_4",
            "Cost": "field_5",
            "Funding": "field_6",
            "Status": "field_7"
        }

        for display_name, value in updated_properties.items():
            internal_name = field_mappings.get(display_name)
            if internal_name:
                if internal_name == "AssignedTo":
                    # Handle person field
                    if value:
                        item.set_property(f"{internal_name}Id", int(value))
                    else:
                        item.set_property(f"{internal_name}Id", None)
                elif internal_name == "field_5":  # Cost field
                    item.set_property(internal_name, float(value) if value else None)
                elif internal_name == "field_4":  # Date field
                    # Ensure date is in the correct format
                    item.set_property(internal_name, value if value else None)
                else:
                    item.set_property(internal_name, value)

        item.update()
        ctx.execute_query()

    except Exception as e:
        logger.error("SharePoint operation update_sharepoint_item failed (%s)", type(e).__name__)
        raise

def add_issue_to_sharepoint(ctx, list_name, title, description, priority, user_id, item_id=None):
    try:
        target_list = ctx.web.lists.get_by_title(list_name)
        
        item_properties = {
            'Title': title,
            'Description': description,
            'Priority': priority,
            'PersonReportingIssueId': user_id
        }
    
        created_item = target_list.add_item(item_properties).execute_query()

    except Exception as e:
        logger.error("SharePoint operation add_issue_to_sharepoint failed (%s)", type(e).__name__)
        raise

def get_user_id(ctx):
    try:
        
        current_user = ctx.web.current_user.get().execute_query()

        return current_user.id

    except Exception as e:
        logger.error("SharePoint operation get_user_id failed (%s)", type(e).__name__)
        raise
