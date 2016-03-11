## Secret bucket
A secret location where Chef validation credentials and terraform.tfstate files
will be stored. This should be locked down with proper access controls. Do NOT
use a root or admin account in any serious environment you care about. **Srsly.**

## Using it:
Do not call `terraform` directly. Instead, use the wrapper script, `poutine`.
This script:
- Sets up the correct remote config management for you
- Passes environment and other important variables to `terraform` for you

Use:

`./poutine <action> <environment> <build_role>`

The resulting environment will be properly tagged in AWS and proper default
values will be chosen for you. To make any changes, you'll want to add/edit
terraform.tfvars under the role in question.

