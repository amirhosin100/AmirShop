
def check_phone(phone):
    success = True
    message = ""

    if not phone.isdigit():
        success = False
        message = "phone must be a number"

    if len(phone) != 11:
        success = False
        message = "phone is not valid"

    if not phone.startswith("09"):
        success = False
        message = "phone must start with <09>"

    return success, message