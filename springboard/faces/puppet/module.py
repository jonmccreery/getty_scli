from springboard.faces import BaseFace
from springboard import VERSION, CONFIG
from jinja2 import Environment, PackageLoader, Template
import getpass
import shutil
import os
import re
import json
import argparse



class PuppetModule(BaseFace):
    # Trailing comma mandatory for single value tuples because python.
    COMMANDS = ('module',)

    def __init__(self):
        super().__init__()
        self.version = VERSION
        self.base_source  = os.path.dirname(os.path.realpath(__file__))
        if 'modulepath' in CONFIG:
            self.cwd=CONFIG['modulepath']
        else: self.cwd=os.getcwd()
        self.hiera_file = {}

    def help(self, parser):
        parser.print_help()
        exit()

    def run_face(self, *args):
        parser = argparse.ArgumentParser()
        parser.add_argument('command', choices=['help', 'generate'], nargs='?')
        parser.add_argument('--hiera', action='store_true', help='Use hiera data provider.')
        parser.add_argument('--nohiera', action='store_true', help='Do not use hiera data provider.')
        parser.add_argument('--name', help='Name of the module.')
        parser.add_argument('--desc', help='Description of the module.')
        parser.add_argument('--git', help='Your git project...')
        parser.add_argument('--modulepath', help='The path to create the module. Defaults to config modulepath or cwd.')
        args = parser.parse_args(args[1:])
        if args.command == 'generate':
            self.generate_module(args)
        else:
            self.help(parser)

    def generate_module(self, args):
        if args.modulepath:
            self.cwd = args.modulepath

        print("Springboard Puppet Module Generator v{}".format(self.version))
        print("------------------------------------------")

        username = getpass.getuser()
        gitlab_url = 'https://gitlab.amer.gettywan.com/springboard_puppet'

        # Main process
        if args.name:
            module_name = args.name
        else:
            module_name = input("What is the module name: ")

        if args.desc:
            module_summary = args.desc
        else:
            module_summary = input("Give a brief summary of this module: ")

        if args.git and args.git != 'sb':
            gitlab_url = args.git
        elif args.git and args.git == 'sb':
            gitlab_url = "https://gitlab.amer.gettywan.com/springboard_puppet"
        else:
            gitlab_url = input("Enter the URL of your Git project (Example: https://gitlab.amer.gettywan.com/springboard_puppet): ")

        # MAGIC
        if gitlab_url == 'sb':
            gitlab_url = "https://gitlab.amer.gettywan.com/springboard_puppet"

        module_source = gitlab_url + "/" + module_name + ".git"
        module_project = gitlab_url + "/" + module_name
        module_issues = gitlab_url + "/" + module_name + "/issues"

        module_data_valid_responses = {
            "yes": True, "y": True, "no": False, "n": False
        }

        if args.hiera and not args.nohiera:
            use_data = 'yes'
        elif args.nohiera and not args.hiera:
            use_data = 'no'
        else:
            use_data = (input("Use in-module hiera data? ")).lower()

        if use_data in module_data_valid_responses:
            if module_data_valid_responses[use_data] == True:
                module_data = '"hiera"'
                self.hiera_file = {
                    "type": "create",
                    "name": "hiera.yaml",
                    "source": os.path.join(self.base_source, 'skel', 'hiera.yaml'),
                    "target": os.path.join(self.cwd, module_name, 'hiera.yaml')
                }
                common_yaml = {
                    "type": "create",
                    "name": "common.yaml",
                    "source": os.path.join(self.base_source, 'skel', 'hieradata', 'common.yaml'),
                    "target": os.path.join(self.cwd, module_name, 'hieradata', 'common.yaml')
                }

            else:
                module_data = 'null'

            dependencies = []
            # Removed dependency support until further notice / need.
            # add_deps = input("Would you like to configure dependencies? ")
            # if module_data_valid_responses[add_deps] == True:
            #     while module_data_valid_responses[add_deps] == True:
            #         name   = input("Name of dependencies (example: puppetlabs-powershell): ")
            #         print("Version requirement can be preceeded by a modifier or pinned to a version:")
            #         print("https://docs.puppet.com/puppet/latest/reference/modules_metadata.html#example")
            #         print("Examples: '1.2.2', >=2.0', '> 1.0.0 < 3.0.0'")
            #         ver    = input("Version Requirement: ")
            #         mydict = {
            #             "name" : name,
            #             "ver"  : ver,
            #         }
            #         dependencies.append(mydict)
            #         add_deps = input("Add more dependencies? ")
            #         if module_data_valid_responses[add_deps] == False:
            #             break
            # else:
            mydict = {
                "name": "puppetlabs-stdlib",
                "ver": ">1.0.0",
            }
            dependencies.append(mydict)

            module_deps = json.dumps(dependencies, indent=4, sort_keys=True)

            # Create a dict for the templates
            meta_vars = {
                "name": module_name,
                "author": username,
                "summary": module_summary,
                "source": module_source,
                "project": module_project,
                "issues": module_issues,
                "data": module_data,
                "deps": module_deps
            }
            if not re.match("^[a-zA-Z0-9_]*$", module_name):
                print("Malformed module name. Please refrain from using spaces or special characters. Aborting!")
                exit
            else:
                print("Generating module skeleton...")
                files = [
                {
                    "type": "create",
                    "name": "metadata.json",
                    "source": self.base_source + '/skel/metadata.json',
                    "target": self.cwd + '/' + module_name + "/metadata.json"
                },
                {
                    "type": "create",
                    "name": "init.pp",
                    "source": self.base_source + "/skel/manifests/role/example.pp",
                    "target": self.cwd + "/" + module_name + "/manifests/role/example.pp"
                },
                {
                    "type": "copy",
                    "name": "Gemfile",
                    "source": self.base_source + "/skel/Gemfile",
                    "target": self.cwd + '/' + module_name + '/Gemfile',
                },
                {
                    "type": "copy",
                    "name": "Rakefile",
                    "source": self.base_source + "/skel/Rakefile",
                    "target": self.cwd + '/' + module_name + '/Rakefile'
                },
                {
                    "type": "copy",
                    "name": "spec_helper.rb",
                    "source": self.base_source + "/skel/spec/spec_helper.rb",
                    "target": self.cwd + '/' + module_name + '/spec/spec_helper.rb'
                },
                {
                    "type": "create",
                    "name": "init_spec.rb",
                    "source": self.base_source + "/skel/spec/classes/init_spec.rb",
                    "target": self.cwd + "/" + module_name + "/spec/classes/init_spec.rb"
                },
                {
                    "type": "copy",
                    "name": "README.md",
                    "source": self.base_source + "/skel/README.md",
                    "target": self.cwd + '/' + module_name + '/README.md'
                },
                {
                    "type": "copy",
                    "name": "CONTRIBUTING.md",
                    "source": self.base_source + "/skel/CONTRIBUTING.md",
                    "target": self.cwd + "/" + module_name + "/CONTRIBUTING.md"
                },
                {
                    "type": "copy",
                    "name": "gitlab-ci.yml",
                    "source": self.base_source + "/skel/.gitlab-ci.yml",
                    "target": self.cwd + "/" + module_name + "/.gitlab-ci.yml"
                }
                ]

            if self.hiera_file:
                files.append(self.hiera_file)
                files.append(common_yaml)

            self.create_directories(module_name)

            for file in files:
                if file['type'] == 'create':
                    self.template_o_rama(file['source'], file['target'], meta_vars)
                elif file['type'] == 'copy':
                    self.copy_o_rama(file['source'], file['target'])

            self.close_up_shop()

    def template_o_rama(self,source,target,meta_vars):
        template_source = open(source)
        template_target = open(target, 'w')
        template_in = Template(template_source.read())
        template_out = template_in.render(meta_vars)
        template_target.write(template_out)
        template_target.close()

    def copy_o_rama(self, source, target):
        shutil.copyfile(source, target)

    def create_directories(self, module_name):
        base_folder = self.cwd + "/" + module_name
        manifests = base_folder + '/manifests'
        spec = base_folder + '/spec'
        unit = base_folder + '/spec/classes'
        spec = base_folder + '/spec'
        hieradata = base_folder + '/hieradata'
        roles = base_folder + '/manifests/role'
        dir_skeleton = (
          base_folder, manifests, spec, unit, hieradata, roles
        )
        for dir in dir_skeleton:
            print("creating {}".format(dir))
            os.mkdir(dir)

    def close_up_shop(self):
        print("Your module has been generated.  I hope you are feeling better.")
