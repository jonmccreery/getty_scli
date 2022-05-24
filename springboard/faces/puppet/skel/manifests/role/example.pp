# Class: {{ name }}::role::example
# Author: {{ author }}
# Project: {{ project }}
class {{ name }}::role::example(
  # Paramterize your class here
  # Enum ['present', 'absent'] $ensure, ## Parameter 'ensure' must be 'present' or 'absent'.
  # String $cheese                      ## Parameter 'cheese' must be a string.
  # Variant[String,Array] $taco         ## Parameter 'taco' can be a string or array.
){
  # Your puppet code here...
  # $tacos = lookup('{{ name }}::tacos') ## a new type of hiera lookup for in-module heira.
  # notify { $tacos : }                 ## returns the value of hiera lookup (in common.yaml)
}
