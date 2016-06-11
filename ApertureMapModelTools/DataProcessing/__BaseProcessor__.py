"""
This is a basic template that is used to add additional processors to
the package.
#
Written By: Matthew Stadelman
Date Written: 2016/02/26
Last Modifed: 2016/02/26
#
"""
#
#
class BaseProcessor:
    r"""
    Only required parameter is a data field object, initializes properties
    defined by subclassses.
    """
    #
    # initializing data
    def __init__(self, field, **kwargs):
        field.copy_data(self)
        self.action = 'base'
        self.args = {}
        self.arg_processors = {}
        self.outfile_name = ''
        self.outfile_content = False
        self.output_key = ''
        self.processed_data = False
        self.validated = False
    #
    def set_args(self, arg_dict, skip_validation=False):
        self.args = dict(arg_dict)
        if (skip_validation):
            self.validated = True
        else:
            self.validated = self.validate_args()
    #
    def validate_args(self):
        r"""
        This steps over the arg processor keys to verify a valid set of
        arguments have been passed to the class.
        """
        # preventing a rerun since validation would fail
        if (self.validated):
          return
        #
        valid = True
        for arg in self.arg_processors.keys():
            processor = self.arg_processors[arg]
            try:
                if (processor.out_type == "single"):
                    input_val = processor.map_func(self.args[arg])
                    if (input_val == ""):
                        raise IndexError
                    self.args[arg] = input_val
                else:
                    input_list = list(filter(None, self.args[arg].split(',')))
                    input_list = list(map(processor.map_func, input_list))
                    #
                    if (len(input_list) < processor.min_num_vals):
                        raise IndexError
                    self.args[arg] = input_list
            #
            except (KeyError, ValueError, IndexError) as err:
                recv = ('' if isinstance(err, KeyError) else self.args[arg])
                self.input_error(err, received=recv, **processor.__dict__)
                valid = False
        #
        return valid
    #
    # generates an error message
    def input_error(self, err=KeyError, field='', received='', expected='', err_desc_str='', **kwargs):
        r"""
        Outputs a useful error message if an input has a missing or invalid entry
        """
        if  (isinstance(err, KeyError)):
            msg = "Error - "+self.action+" requires "+field+"="+expected+" argument."
        elif (isinstance(err, IndexError)):
            msg = "Error - "+self.action+" requires "+field+"="+expected+" "+err_desc_str+". recieved: '"+received+"'"
        elif (isinstance(err, ValueError)):
            msg = "Error - "+self.action+" requires "+field+"="+expected+" "+err_desc_str+". recieved: '"+received+"'"
        else:
            print("Unhandled eroor type encountered.")
            raise err
        #
        print(msg)
    #
    def process(self, **kwargs):
        r"""
        Calls the subclassed routine process_data to create outfile content
        """
        if (not self.validated):
            print('Error arguments have not been validated. Run .set_args(arg_dict) method first.')
            return
        #
        self.process_data(**kwargs)
        #
    #
    def process_data(self, **kwargs):
        r"""
        Not implemented
        """
        raise NotImplementedError('This method must be implemented by a specific ' +
                                  'data processing class')
    #
    def gen_output(self, **kwargs):
        r"""
        Calls the subclassed routine output_data to create outfile content
        """
        if (not self.processed_data):
            print('Error no data has been processed. Run .process() method first')
            return
        #
        self.output_data(**kwargs)
        #
    #
    def output_data(self, **kwargs):
        r"""
        Not implemented
        """
        raise NotImplementedError('This method must be implemented by a specific ' +
                                  'data processing class')
    #
    def copy_processed_data(self, data_dict, alt_key=False):
        r"""
        Copys the current processed data array to a dict object using a
        key defined in the subclass initialization. If alt key is specifi
        """
        if (not self.outfile_content):
            print('Error output content has not been generated. Run .gen_output() method first')
            return
        #
        key = alt_key if alt_key else self.output_key
        data_dict[key] = self.processed_data
    #
    def print_data(self):
        r"""
        Writes the data processor's data the screen
        """
        if (not self.outfile_content):
            print('Error output content has not been generated. Run .gen_output() method first')
            return
        #
        print(self.outfile_content)
        print('')
    #
    def write_data(self):
        r"""
        Writes the data processor's data to its outfile
        """
        if (not self.outfile_content):
            print('Error output content has not been generated. Run .gen_output() method first')
            return
        #
        with open(self.outfile_name, 'w') as f:
            f.write(self.outfile_content)
        print("Output saved as: "+self.outfile_name)
    #
#
#
