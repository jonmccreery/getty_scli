require 'spec_helper'
describe '{{ name }}' do
  context 'with default values for all parameters' do
    it { should contain_class('{{ name }}') }
  end

end
