from django.shortcuts import render
from django.http import HttpResponse
import fitz # PyMuPDF
import os
import re
from datetime import datetime 
from .forms import PdfUploadForm
from .models import Complaint # Import your new model

def index(request):
    return render(request, 'pdfReader/index.html', {})


def upload_pdf_view(request):
    if request.method == "POST":
        form = PdfUploadForm(request.POST, request.FILES) # Instantiate form with POST data and files
        if form.is_valid():
            uploaded_file = form.cleaned_data["pdf_file"]

            # --- Important: Handle the uploaded file ---
            # Option 1: Save the file temporarily to disk to process it
            # This is often necessary for libraries like fitz which expect a file path.
            # You might want a dedicated 'media' directory for uploads in a real project.
            temp_file_path = f"/tmp/{uploaded_file.name}" # Or use Django's MEDIA_ROOT
            with open(temp_file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Option 2: Pass file object directly if library supports it (less common for PDF)
            # This depends on the PDF library's capabilities. fitz.open() can take a BytesIO object.
            # from io import BytesIO
            # pdf_bytes = BytesIO(uploaded_file.read())
            # extracted_data = extract_complaint_details(pdf_bytes) # if extract_pdf can handle BytesIO

            # Process the PDF using your extraction function
            extracted_data = extract_pdf(temp_file_path)

            #if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

            # --- Step to save data to the database ---
            try:
                # Convert extracted strings to appropriate types for the model
                # Use .get() with a default of None to handle missing keys gracefully
                report_id_val = extracted_data.get('Report ID')
                category_val = extracted_data.get('Category')
                status_val = extracted_data.get('Status')
                priority_val = extracted_data.get('Priority')
                assigned_to_val = extracted_data.get('Assigned to')
                reported_by_val = extracted_data.get('Reported by')
                location_val = extracted_data.get('Location')
                contact_email_val = extracted_data.get('Contact Email')
                contact_phone_val = extracted_data.get('Contact Phone')
                details_val = extracted_data.get('Details')
                action_taken_val = extracted_data.get('Action Taken')
                resolution_val = extracted_data.get('Resolution')

                # Parse date/time fields. Adjust format string if needed.
                # Example format: '18 Jul 2025 00:00AM' -> '%d %b %Y %H:%M%p'
                due_date_str = extracted_data.get('Due date')
                due_date_val = None
                if due_date_str:
                    try:
                        due_date_val = datetime.strptime(due_date_str, '%d %b %Y %H:%M%p')
                    except ValueError:
                        print(f"Warning: Could not parse Due date: {due_date_str}")

                reported_on_str = extracted_data.get('Reported on')
                reported_on_val = None
                if reported_on_str:
                    try:
                        # Assuming '17 Jun 2025 16:50PM' for Reported on
                        reported_on_val = datetime.strptime(reported_on_str, '%d %b %Y %H:%M%p')
                    except ValueError:
                         print(f"Warning: Could not parse Reported on date: {reported_on_str}")

                occurred_at_str = extracted_data.get('Occurred at')
                occurred_at_val = None
                if occurred_at_str:
                    try:
                        # Assuming '17 Jun 2025 16:33PM' for Occurred at
                        occurred_at_val = datetime.strptime(occurred_at_str, '%d %b %Y %H:%M%p')
                    except ValueError:
                         print(f"Warning: Could not parse Occurred at date: {occurred_at_str}")

                closed_date_str = extracted_data.get('Closed Date')
                closed_date_val = None
                if closed_date_str:
                    try:
                        closed_date_val = datetime.strptime(closed_date_str, '%d %b %Y %H:%M%p')
                    except ValueError:
                        print(f"Warning: Could not parse Closed Date: {closed_date_str}")


                # Create a new Complaint object and save it to the database
                # Use update_or_create if you want to update an existing record based on report_id
                # Otherwise, create a new one each time:
                
                # Check if a complaint with this report_id already exists
                # This prevents duplicate entries if the report_id is unique
                if report_id_val:
                    complaint, created = Complaint.objects.update_or_create(
                        report_id=report_id_val,
                        defaults={
                            'category': category_val,
                            'status': status_val,
                            'priority': priority_val,
                            'assigned_to': assigned_to_val,
                            'due_date': due_date_val,
                            'reported_by': reported_by_val,
                            'reported_on': reported_on_val,
                            'occurred_at': occurred_at_val,
                            'location': location_val,
                            'contact_email': contact_email_val,
                            'contact_phone': contact_phone_val,
                            'closed_date': closed_date_val,
                            'details': details_val,
                            'action_taken': action_taken_val,
                            'resolution': resolution_val,
                        }
                    )
                    if created:
                        print(f"New complaint created: {complaint.report_id}")
                    else:
                        print(f"Complaint updated: {complaint.report_id}")
                else:
                    # Handle case where report_id might be missing or not unique
                    # Or, if report_id is not guaranteed unique, just create:
                    complaint = Complaint.objects.create(
                        category=category_val,
                        status=status_val,
                        priority=priority_val,
                        assigned_to=assigned_to_val,
                        due_date=due_date_val,
                        reported_by=reported_by_val,
                        reported_on=reported_on_val,
                        occurred_at=occurred_at_val,
                        location=location_val,
                        contact_email=contact_email_val,
                        contact_phone=contact_phone_val,
                        closed_date=closed_date_val,
                        details=details_val,
                        action_taken=action_taken_val,
                        resolution=resolution_val,
                        # report_id will be null if report_id_val is None
                        report_id=report_id_val # Include even if it's None for consistency
                    )
                    print(f"Complaint saved with ID: {complaint.pk}")


                # Render a success page or redirect
                return render(request, "pdfReader/success.html", {"extracted_data": extracted_data})

            except Exception as e:
                # Handle database saving errors
                print(f"Error saving data to database: {e}")
                form.add_error(None, f"Error saving data: {e}") # Add a non-field error to the form
                return render(request, "pdfReader/index.html", {"form": form})

        else:
            # Form is not valid, re-render with errors
            return render(request, "pdfReader/index.html", {"form": form})
    else:
        # This is a GET request, display the empty form
        form = PdfUploadForm()
    return render(request, "pdfReader/index.html", {"form": form})


def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    page1 = doc.load_page(0)
    page2 = doc.load_page(1)

    

    text = page1.get_text()
    text2 = page2.get_text()

    lines = text.splitlines()
    lines2 = text2.splitlines()

    doc.close()

    details_labels = ["Category", "Status", "Site", "Assignee", "Priority",
    "Unique Id", "Due date", "Reported by", "Reported on",
    "Occurred at" ]

    details = {}

    # extract complain details in the first page
    for label in details_labels:
        idx = lines.index(label)
        details[label] = lines[idx + 1]

    # extract the deatils of the second page
    question_page2 = "Answered the question: What is the specific cleanliness issue that needs to be addressed (include exact location)?"

    regex = rf"{question_page2}(.*?){details[details_labels[7]]}"
    match = re.search(regex, text2, re.DOTALL)

    if match:
        details['Details'] = match.group(0)

    return details