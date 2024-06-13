from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                "class": "custom-file-input",
                "accept": ".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "id": "customFile",
            }
        ),
    )