# face: config

## Description:

Get and set the Springboard CLI configuration settings.

## Usage

### Retreive Settings

	> springboard config print

### Create new or modify existing key/value pair

	> springboard config set --key <key> --value <value>

### Wipe a setting

	> springboard config set --key <key>

# face: module

## Description:

Generates a puppet module per best practices and internal standards.  You will be prompted for values if they are not specified.

## Usage

### Walk through the Module Generation Wizard(tm)

        > springboard module generate

### Optional Parameters
        --name NAME             Name of the module.
        --desc DESC             Description of the module.
        --hiera                 Use hiera data provider.
        --nohiera               Do not use hiera data provider.
        --git <url>             Your git project (i.e. https://gitlab.amer.gettywan.com/puppet_springboard)
        --modulepath <path>     Where to create the module (i.e. C:\code\puppetmodules) 