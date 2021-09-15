set -ev
bundle exec jekyll build
rsync --archive --compress --progress --partial _site/ sciolizer@sciolizer.com:/home/sciolizer/sciolizer.com
