#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def test_github_config():
    """Test GitHub configuration files"""

    print("🔍 Testing GitHub configuration...")

    # Check if .github directory exists
    github_dir = ".github"
    if os.path.exists(github_dir):
        print(f"✅ {github_dir}/ directory exists")
    else:
        print(f"❌ {github_dir}/ directory missing")
        return False

    # Check CODEOWNERS file
    codeowners_file = os.path.join(github_dir, "CODEOWNERS")
    if os.path.exists(codeowners_file):
        with open(codeowners_file, 'r') as f:
            content = f.read()
            if '@Nsfr750' in content:
                print("✅ CODEOWNERS file exists and has proper ownership")
            else:
                print("❌ CODEOWNERS file missing ownership rules")
    else:
        print("❌ CODEOWNERS file missing")

    # Check workflows directory
    workflows_dir = os.path.join(github_dir, "workflows")
    if os.path.exists(workflows_dir):
        workflow_files = [f for f in os.listdir(workflows_dir) if f.endswith('.yml')]
        if workflow_files:
            print(f"✅ {len(workflow_files)} workflow files found: {workflow_files}")
        else:
            print("❌ No workflow files found")
    else:
        print("❌ workflows directory missing")

    # Check issue templates
    issue_template_dir = os.path.join(github_dir, "ISSUE_TEMPLATE")
    if os.path.exists(issue_template_dir):
        template_files = [f for f in os.listdir(issue_template_dir) if f.endswith('.yml')]
        if template_files:
            print(f"✅ {len(template_files)} issue template files found: {template_files}")
        else:
            print("❌ No issue template files found")
    else:
        print("❌ ISSUE_TEMPLATE directory missing")

    # Check pull request template
    pr_template = os.path.join(github_dir, "PULL_REQUEST_TEMPLATE.md")
    if os.path.exists(pr_template):
        print("✅ Pull request template exists")
    else:
        print("❌ Pull request template missing")

    print("\n✅ GitHub configuration test completed!")
    return True

if __name__ == "__main__":
    test_github_config()
