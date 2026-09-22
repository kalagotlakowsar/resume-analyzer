from django import forms
from .models import Resume, JobRole

class ResumeUploadForm(forms.ModelForm):
    job_role = forms.ModelChoiceField(
        queryset=JobRole.objects.all(),
        required=False,
        empty_label="-- Select a Target Job Role --",
        widget=forms.Select(attrs={'class': 'form-select select2-enable', 'id': 'id_job_role'})
    )
    custom_role_title = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Senior Machine Learning Engineer',
            'id': 'id_custom_role_title'
        })
    )
    custom_job_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Paste the full Job Description (responsibilities, required qualifications, tech stack) here...',
            'id': 'id_custom_job_description'
        })
    )

    class Meta:
        model = Resume
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Software_Engineer_Resume_2026'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx',
                'id': 'resume_file_input'
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx']:
                raise forms.ValidationError("Only PDF (.pdf) and Word (.docx) files are supported.")
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 5 MB.")
        return file
