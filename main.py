import os
import requests
import re
import smtplib
from email.message import EmailMessage
from urllib.parse import urljoin, urlparse

WEB_URL = "https://downloads.remarkable.com/latest/windows"
VERSION_FILE = "version.txt"


def send_email_notification(
    subject,
    body,
    to_email,
    from_email,
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_password,
):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")


def get_download_url(web_url):
    response = requests.get(web_url)
    return response.url if response.ok else None
    ###
    html = response.text.replace("\n", " ")
    match = re.search(
        r'<a[^>]*href="([^"]+)"[^>]*>Download\s+Smokeball\s+-\s+AU', html, re.IGNORECASE
    )

    if match:
        return urljoin(web_url, match.group(1))

    return None
    ###


def get_filename_from_url(url):
    response = requests.head(url, allow_redirects=True)
    cd = response.headers.get("Content-Disposition", "")
    match = re.search(r'filename="?([^";\r\n]+)"?', cd)

    if match:
        return match.group(1)

    return os.path.basename(urlparse(response.url).path)


def read_version_file(version_file):
    if not os.path.exists(version_file):
        return None
    with open(version_file, "r") as file:
        return file.read().strip()


def write_version_file(version_file, version):
    with open(version_file, "w") as file:
        file.write(version)


def main():
    url = get_download_url(WEB_URL)
    if not url:
        print("Download URL not found. Exiting.")
        return

    print(f"Download URL: {url}")
    filename = get_filename_from_url(url)

    if not filename:
        print("Could not determine filename from URL. Exiting.")
        return

    print(f"Latest version filename: {filename}")

    stored_version = read_version_file(VERSION_FILE)

    if stored_version == filename:
        print("No new version. Exiting.")
        return
    else:
        print("New version found!")
        write_version_file(VERSION_FILE, filename)
        send_email_notification(
            subject="New Smokeball Version Available",
            body=f"A new version of Smokeball is available: {filename}\nDownload it here: {url}",
            to_email=os.getenv("TO_EMAIL"),
            from_email=os.getenv("FROM_EMAIL"),
            smtp_server=os.getenv("SMTP_SERVER"),
            smtp_port=int(os.getenv("SMTP_PORT", 587)),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_password=os.getenv("SMTP_PASSWORD"),
        )


if __name__ == "__main__":
    main()
