import logging
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.runtime.client_request_exception import ClientRequestException

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# SharePoint configuration
site_url = 'https://academiedavinci.sharepoint.com/sites/ADVTechHelp'
inventory_list_name = 'Inventory'

def test_sharepoint_connection(username, password):
    try:
        user_credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(user_credentials)
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        return True
    except ClientRequestException as e:
        logger.error(f"ClientRequestException: {str(e)}")
        if isinstance(e.response, HttpResponse):
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.content}")
        if "AADSTS50126" in str(e):
            raise ValueError("Invalid username or password. Please check your credentials and try again.")
        else:
            raise ValueError(f"An error occurred while connecting to SharePoint: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise ValueError(f"An unexpected error occurred: {str(e)}")

def get_sharepoint_list_items(username, password, list_name, page_size=100, page_number=1, field=None, value=None):
    try:
        user_credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(user_credentials)
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
        logger.debug(f"Retrieved items: {all_items}")
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
        logger.error(f"Error in get_sharepoint_list_items: {str(e)}", exc_info=True)
        raise

def get_sharepoint_item(username, password, list_name, item_id):
    try:
        user_credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(user_credentials)
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

        logger.debug(f"Retrieved item (ID: {item_id}): {mapped_item}")
        return mapped_item
    except Exception as e:
        logger.error(f"Error in get_sharepoint_item: {str(e)}", exc_info=True)
        raise

def update_sharepoint_item(username, password, list_name, item_id, updated_properties):
    try:
        user_credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(user_credentials)
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
        logger.debug(f"Updated item (ID: {item_id})")
    except Exception as e:
        logger.error(f"Error in update_sharepoint_item: {str(e)}", exc_info=True)
        raise

def add_issue_to_sharepoint(username, password, list_name, title, description, priority, user_id, item_id=None):
    try:
        user_credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(user_credentials)
        target_list = ctx.web.lists.get_by_title(list_name)
        
        item_properties = {
            'Title': title,
            'Description': description,
            'Priority': priority,
            'PersonReportingIssueId': user_id
        }
    
        created_item = target_list.add_item(item_properties).execute_query()
        
        logger.debug(f"Created issue in Tickets list: {title}")

    except Exception as e:
        logger.error(f"Error in add_issue_to_sharepoint: {str(e)}", exc_info=True)
        raise

def get_user_id(username, password, user_email):
    try:
        user_credentials = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(user_credentials)
        
        current_user = ctx.web.current_user.get().execute_query()
        logger.debug(f"Current user: {current_user.properties}")
        
        return current_user.id

    except Exception as e:
        logger.error(f"Error in get_user_id: {str(e)}", exc_info=True)
        raise
