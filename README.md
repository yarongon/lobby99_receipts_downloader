# Lobby 99 Receipts Downloader

## Introduction
The Lobby 99 Receipts Downloader is a utility designed to streamline the process of retrieving receipts sent by Lobby 99 via email at the end of each year.
Typically, these receipts are provided as download links within the email, making the manual downloading process cumbersome and time-consuming.
This script simplifies the task by automating the retrieval of all associated files for your convenience.

## Usage
To utilize this tool effectively, follow these straightforward steps:

1. Download the email containing the receipts and save it as an `eml` file, such as `email.eml`.

2. Execute the script using the following command:
   ```shell
   $ python dl_lobby99_receipts.py email.eml
   ```

   This command will initiate the downloading process, and all retrieved PDF files will be conveniently stored in your current directory.

## How does it Work
The email comprises HTML code. Within this code, the script identifies all the URLs enclosed within `a` tags. It then filters and retains only those URLs whose descriptions include the term `pdf`.
It's important to note that these URLs are not direct links to the PDF files; instead, the script follows the redirection in each link to obtain the actual URL pointing to the PDF file.

Enjoy!