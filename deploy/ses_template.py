import boto3

client = boto3.client("ses")


def deploy_template(template_name, subject, html, text):
    try:
        response = client.get_template(TemplateName=template_name)
        if "Template" in response:
            client.update_template(
                Template={
                    "TemplateName": template_name,
                    "SubjectPart": subject,
                    "HtmlPart": html,
                    "TextPart": text,
                }
            )
            return f"Template {template_name} already exists, updated successfully"
    except client.exceptions.TemplateDoesNotExistException:
        client.create_template(
            Template={
                "TemplateName": template_name,
                "SubjectPart": subject,
                "HtmlPart": html,
                "TextPart": text,
            }
        )
    
    return f"Template {template_name} created successfully"


def send_email(template_name, sender, recipient, subject, body):
    client.send_templated_email(
        Source=sender,
        Destination={"ToAddresses": [recipient]},
        Template=template_name,
        TemplateData=body,
    )
    return f"Email sent successfully"


body_mail ="""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="x-ua-compatible" content="ie=edge" />
        <title>Email Confirmation</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style type="text/css">
            @media screen {
                @font-face {
                    font-family: "Source Sans Pro";
                    font-style: normal;
                    font-weight: 400;
                    src: local("Source Sans Pro Regular"),
                        local("SourceSansPro-Regular"),
                        url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff)
                            format("woff");
                }
                @font-face {
                    font-family: "Source Sans Pro";
                    font-style: normal;
                    font-weight: 700;
                    src: local("Source Sans Pro Bold"),
                        local("SourceSansPro-Bold"),
                        url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff)
                            format("woff");
                }
            }
            body,
            table,
            td,
            a {
                -ms-text-size-adjust: 100%;
                -webkit-text-size-adjust: 100%;
            }
            table,
            td {
                mso-table-rspace: 0pt;
                mso-table-lspace: 0pt;
            }
            img {
                -ms-interpolation-mode: bicubic;
            }
            a[x-apple-data-detectors] {
                font-family: inherit !important;
                font-size: inherit !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                color: inherit !important;
                text-decoration: none !important;
            }
            div[style*="margin: 16px 0;"] {
                margin: 0 !important;
            }
            body {
                width: 100% !important;
                height: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            table {
                border-collapse: collapse !important;
            }
            a {
                color: #1a82e2;
            }
            img {
                height: auto;
                line-height: 100%;
                text-decoration: none;
                border: 0;
                outline: none;
            }
        </style>
    </head>
    <body style="background-color: #e9ecef">
        <div
            class="preheader"
            style="
                display: none;
                max-width: 0;
                max-height: 0;
                overflow: hidden;
                font-size: 1px;
                line-height: 1px;
                color: #fff;
                opacity: 0;
            "
        >
            A visitor needs your approval
        </div>
        <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table
                        border="0"
                        cellpadding="0"
                        cellspacing="0"
                        width="100%"
                        style="max-width: 600px"
                    >
                        <tr>
                            <td
                                align="center"
                                valign="top"
                                style="padding: 36px 24px"
                            >
                                <img
                                src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Watchguard_logo.svg/2560px-Watchguard_logo.svg.png"
                                alt="Logo" border="0" style="display: block;
                                width: 128px; max-width:128px; height: auto"
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table
                        border="0"
                        cellpadding="0"
                        cellspacing="0"
                        width="100%"
                        style="max-width: 600px"
                    >
                        <tr>
                            <td
                                align="left"
                                bgcolor="#ffffff"
                                style="
                                    padding: 36px 24px 0;
                                    font-family: 'Source Sans Pro', Helvetica,
                                        Arial, sans-serif;
                                    border-top: 3px solid #d4dadf;
                                "
                            >
                                <h1
                                    style="
                                        margin: 0;
                                        font-size: 32px;
                                        font-weight: 700;
                                        letter-spacing: -1px;
                                        line-height: 48px;
                                    "
                                >
                                    A visitor has arrived!!
                                </h1>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td align="center" bgcolor="#e9ecef">
                    <table
                        border="0"
                        cellpadding="0"
                        cellspacing="0"
                        width="100%"
                        style="max-width: 600px"
                    >
                        <tr>
                            <td
                                align="left"
                                bgcolor="#ffffff"
                                style="
                                    padding: 24px;
                                    font-family: 'Source Sans Pro', Helvetica,
                                        Arial, sans-serif;
                                    font-size: 16px;
                                    line-height: 24px;
                                "
                            >
                                <p style="margin: 0">
                                    A visitor has arrived and is waiting for
                                    your approval. Please take a look at the
                                    details below and take action.
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <td
                                align="left"
                                bgcolor="#ffffff"
                                style="
                                    padding: 24px;
                                    font-family: 'Source Sans Pro', Helvetica,
                                        Arial, sans-serif;
                                    font-size: 16px;
                                    line-height: 24px;
                                "
                            >
                                <p style="margin: 0">
                                    <strong>Name:</strong> {{name}}
                                </p>
                                <p style="margin: 0">
                                    <strong>Company:</strong> {{organization}}
                                </p>
                                <p style="margin: 0">
                                    <strong>Reason for visit:</strong>
                                    {{purpose}}
                                </p>
                                <p style="margin: 0">
                                    <strong>Phone number </strong> {{ph_number}} 
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <td align="left" bgcolor="#ffffff">
                                <table
                                    border="0"
                                    cellpadding="0"
                                    cellspacing="0"
                                    width="100%"
                                >
                                    <tr>
                                        <td
                                            align="center"
                                            bgcolor="#ffffff"
                                            style="padding: 12px"
                                        >
                                            <table
                                                border="0"
                                                cellpadding="0"
                                                cellspacing="0"
                                            >
                                                <tr>
                                                    <td
                                                        align="center"
                                                        style="
                                                            border-radius: 6px;
                                                        "
                                                    >
                                                        <a
                                                            href="https://ryfhm9zfki.execute-api.ap-south-1.amazonaws.com/dev/approval/{{visit_id}}?access_token={{access_token}}&action=approved"
                                                            class="approve"
                                                            style="
                                                                display: inline-block;
                                                                padding: 16px
                                                                    36px;
                                                                font-family: 'Source Sans Pro',
                                                                    Helvetica,
                                                                    Arial,
                                                                    sans-serif;
                                                                font-size: 16px;
                                                                color: #ffffff;
                                                                text-decoration: none;
                                                                border-radius: 6px;
                                                                background-color: #1a82e2;
                                                                margin: 5px;
                                                            "
                                                            >Approve</a
                                                        >
                                                    </td>
                                                    <td
                                                        align="center"
                                                        style="
                                                            border-radius: 6px;
                                                        "
                                                    >
                                                        <a
                                                            href="https://blmdrybz1c.execute-api.ap-south-1.amazonaws.com/dev/approval/{{visit_id}}?access_token={{access_token}}&action=rejected"
                                                            class="reject"
                                                            style="
                                                                display: inline-block;
                                                                padding: 16px
                                                                    36px;
                                                                font-family: 'Source Sans Pro',
                                                                    Helvetica,
                                                                    Arial,
                                                                    sans-serif;
                                                                font-size: 16px;
                                                                color: #ffffff;
                                                                text-decoration: none;
                                                                border-radius: 6px;
                                                                background-color: red;
                                                                margin: 5px;
                                                            "
                                                            >Reject&nbsp;</a
                                                        >
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <tr>
                            <td
                                align="left"
                                bgcolor="#ffffff"
                                style="
                                    padding: 24px;
                                    font-family: 'Source Sans Pro', Helvetica,
                                        Arial, sans-serif;
                                    font-size: 16px;
                                    line-height: 24px;
                                    border-bottom: 3px solid #d4dadf;
                                "
                            ></td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td align="center" bgcolor="#e9ecef" style="padding: 24px">
                    <table
                        border="0"
                        cellpadding="0"
                        cellspacing="0"
                        width="100%"
                        style="max-width: 600px"
                    >
                        <tr>
                            <td
                                align="center"
                                bgcolor="#e9ecef"
                                style="
                                    padding: 12px 24px;
                                    font-family: 'Source Sans Pro', Helvetica,
                                        Arial, sans-serif;
                                    font-size: 14px;
                                    line-height: 20px;
                                    color: #666;
                                "
                            ></td>
                    </tr>
                        <tr>
                            <td
                                align="center"
                                bgcolor="#e9ecef"
                                style="
                                    padding: 12px 24px;
                                    font-family: 'Source Sans Pro', Helvetica,
                                        Arial, sans-serif;
                                    font-size: 14px;
                                    line-height: 20px;
                                    color: #666;
                                "
                            ></td>
                        </tr>
                    </table>
                </td>
            </tr>
    </body>
</html>
"""

def send_verification_mails(emails):
    for email in emails:
        client.verify_email_identity(EmailAddress=email)

if __name__ == "__main__":
    print(deploy_template("vms_email_template-test", "A visitor needs your approval", body_mail, "A visitor needs your approval"))
    