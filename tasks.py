from robocorp.tasks import task
from robocorp import browser
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
#from RPA.HTTP import HTTP
import requests
import shutil


#order_website = "https://robotsparebinindustries.com/#/robot-order"
#orders_file = "https://robotsparebinindustries.com/orders.csv"
#page=browser.page()

@task

def order_robots_from_RobotSpareBin():
    

    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    open_robot_order_website()
    download_orders_file()
    read_csv_as_table()
    archive_receipts()
    clean_up()


def open_robot_order_website():
    
    """Navigates to the given URL"""

    browser.configure(browser_engine="chrome", slowmo=100)
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

    page=browser.page()
    page.click('text=OK')

def download_orders_file():

    """Download .csv file from the given URL"""

    #http = HTTP()
    #http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)

    download=requests.get("https://robotsparebinindustries.com/orders.csv")
    with open("orders.csv", "wb") as file:
        file.write(download.content)

def order_another_bot():

    """Clicks on orther another bot button"""
    
    page = browser.page()
    page.click("#order-another")

def button_ok():

    """Clicks OK after every order"""

    page=browser.page()
    page.click('text=OK')

def fill_and_order_robot_parts(order):

    """Fills robot order details and clicks the 'Order' button"""

    page=browser.page()

    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    #head_number = order["Head"]
    #page.select_option("#head", head_names.get(head_number))
    page.select_option("#head", head_names.get(order["Head"]))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            order_another_bot()
            button_ok()
            break


def store_receipt_as_pdf(order_number):

    """This stores robot order receipt as PDF"""

    page = browser.page()
    
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    #pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def read_csv_as_table():

    """Read data from csv and fill in robot order form"""

    csv_file=Tables()

    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_and_order_robot_parts(order)

def screenshot_robot(order_number):

    """Takes screenshot of the ordered bot image"""

    page = browser.page()
    
    #screenshot_path = "output/screenshots/{0}.png".format(order_number)
    screenshot_path = f"output/screenshots/{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):

    """Embeds the screenshot to the receipe"""

    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, 
                                   source_path=pdf_path, 
                                   output_path=pdf_path)
    
def archive_receipts():
    
    """Archive all the receipts in to Zip file"""

    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def clean_up():

    """Cleans up the folders where receipts and screenshots are saved."""

    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")