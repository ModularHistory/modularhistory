# If necessary, replace the dot (first arg) with the path to the virtual Python environment (or its parent)
find . -type f -name "*.py" -print0 | xargs -0 sed -i '' -e 's/from django.utils import six/import six/g';
find . -type f -name "*.py" -print0 | xargs -0 sed -i '' -e 's/, python_2_unicode_compatible//g';
find . -type f -name "*.py" -print0 | xargs -0 sed -i '' -e 's/@python_2_unicode_compatible//g';
