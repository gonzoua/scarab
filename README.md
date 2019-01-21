# Overview
scarab is a CLI tool to automate some of the Bugzilla-related workflows in the FreeBSD project.

# Installation
```
# Install python3 and pip 
sudo pkg install python3 py36-pip

# Install latest release of scarab
pip-3.6 install --user scarab
# .. or current WIP
git clone https://github.com/gonzoua/scarab.git
cd scarab
pip-3.6 install --user -e .

# Add ~/.local/bin to PATH
# for bash:
export PATH=$PATH:~/.local/bin
# for tcsh/csh:
setenv PATH $PATH\:$HOME/.local/bin

# test setup
scarab products
```

# Settings
scarab config file has a generic section-based INI format. A section starts with [sectionname]  and consists of key/value pairs separated by "=". Value is the part of the line after "=" with leading and trailing spaces removed.  If there are spaces in the middle of the string, they're treated as a part of the value.

## [default] section

### url

Base URL  for Bugzilla setup. By default, it's FreeBSD's Bugzilla instance https://bugs.freebsd.org/bugzilla/

### api_key

API key for the operations. Normally commands that do not modify Bugzilla's state like `fetch`, `fetchall`, `file` do not require it, unless you're trying to access PRs with restricted access. To generate new API key login to your Bugzilla instance, click on "Preferences" link then select "API keys" tab, check "Generate a new API key ..." checkbox, provide an optional description and click "Submit Changes"

## [template:NNN] sections

Templates are sets of fields that you can use when submitting new PRs instead of specifying them individually as command-line arguments. Valid keys for this kind of section are: `product`, `component`, `version`, `platform`, `severity`. Possible values depend on the actual Bugzilla instance configuration. Some of them can be inspected using `products` command. The part of the section name after the colon is used as an argument to `-t` switch of the `submit` command as a shorthand for multiple switches. For more examples of template usage see [scarabrc](examples/scarabrc).

# Commands
## attach
attach [-h] [-s SUMMARY] [-c COMMENT | -F COMMENT_FILE] [-t CONTENT_TYPE] attachment pr

Attach file specified by the path `attachment` to the bug with id `pr`. If no summary provided the file name is used as a summary. If neither `-c` nor `-F` is specified tool will invoke editor so a user can enter the comment text. File content type is detecting automatically using libmagic and can be overridden by `-t` command-line switch.

## fetch
fetch [-h] [-o OUTPUT] attachment_id

Download attachment with the id `attachment_id` to the file specified by `-o` command-line switch or to the file in the current directory with the same name as an attachment.

## fetchall
fetchall [-h] bug_id

Download all non-obsolete attachments of the bug with id `bug_id` to the current directory.

## files
files [-h] [-a] [-s] bug_id

Show list of the files attached to the bug with id `bug_id`. Unless `-a` is specified only non-obsolete attachments are displayed. When `-s` is used, the summary of the attachment is displayed instead of the file name.

## info
info [-h] bug_id

Display information for bug bug_id including bug description

## products
products [-h]

Display list of products, their components and versions

## submit
submit [-h] [-t TEMPLATES] [-p PRODUCT] [-m COMPONENT] [-v VERSION] [-c COMMENT | -F COMMENT_FILE] -s SUMMARY [-C CC] [-P PLATFORM] [-S SEVERITY]

Submit new bug with the summary specified by `-s` command-line switch. Mandatory fields `product`, `component`, `version` should be specified either by command-line switches or as values in templates sections. If multiple templates are specified in one invocation, they are merged with fields each following template overriding values present in the previous ones. Values for the fields provided as a command-line switch override the values in the templates.

## update
update [-h] [-s STATUS] [-r RESOLUTION] [-a ASSIGNED_TO] [-C ADD_CC] [-X REMOVE_CC] [-c COMMENT | -F COMMENT_FILE] bug_id

Update fields in existing PR. If neither `-c` nor `-F` specified no comment is posted with the change. `-C` and `-X` can be specified multiple times to add/remove more than one user.

# Development
To run the scarab command using checked out version of the repo use `python3 -m scarab.cli ...` command
