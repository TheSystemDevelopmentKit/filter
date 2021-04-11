"""
========
Filter
========

Filter model template The System Development Kit

Current docstring documentation style is Numpy
https://numpydoc.readthedocs.io/en/latest/format.html

For reference of the markup syntax
https://docutils.sourceforge.io/docs/user/rst/quickref.html

This text here is to remind you that documentation is iportant.
However, youu may find it out the even the documentation of this 
entity may be outdated and incomplete. Regardless of that, every day 
and in every way we are getting better and better :).

Initially written by Marko Kosunen, marko.kosunen@aalto.fi, 2017.


Role of section 'if __name__=="__main__"'
--------------------------------------------

This section is for self testing and interfacing of this class. The content of it is fully 
up to designer. You may use it for example to test the functionality of the class by calling it as
``pyhon3.6 __init__.py``

or you may define how it handles the arguments passed during the invocation. In this example it is used 
as a complete self test script for all the simulation models defined for the filter. 

"""

import os
import sys
if not (os.path.abspath('../../thesdk') in sys.path):
    sys.path.append(os.path.abspath('../../thesdk'))

from thesdk import *
from spice import *

import numpy as np

class filter(spice,thesdk):
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg): 
        """ Inverter parameters and attributes

            model : string
                Default 'py' for Python. See documentation of thsdk package for more details.
        
            par : boolean
            Attribute to control parallel execution. HOw this is done is up to designer.
            Default False

            queue : array_like
            List for return values in parallel processing. This list is read by the process in parent to get the values 
            evalueted by the instance copies created during the parallel processing loop.

        """
        self.print_log(type='I', msg='Initializing %s' %(__name__)) 
        self.proplist = [ 'Rs' ];    # Properties that can be propagated from parent
        self.Capval =  1e-12;            # Sampling frequency
        self.Rval = 1e3
        self.IOS=Bundle()
        self.IOS.Members['inniputti']=IO() # Pointer for input data
        self.IOS.Members['outtiputti']= IO()
        # File for control is created in controller
        self.model='py';             # Can be set externally, but is not propagated
        self.par= False              # By default, no parallel processing
        self.queue= []               # By default, no parallel processing

        # this copies the parameter values from the parent based on self.proplist
        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;

        self.init()

    def init(self):
        """ Method to re-initialize the structure if the attribute values are changed after creation.

        """
        pass #Currently nohing to add

    def main(self):
        ''' The main python description of the operation. Contents fully up to designer, however, the 
        IO's should be handled bu following this guideline:
        
        To isolate the internal processing from IO connection assigments, 
        The procedure to follow is
        1) Assign input data from input to local variable
        2) Do the processing
        3) Assign local variable to output

        '''
        pass
    def run(self,*arg):
        ''' The default name of the method to be executed. This means: parameters and attributes 
            control what is executed if run method is executed. By this we aim to avoid the need of 
            documenting what is the execution method. It is always self.run. 

            Parameters
            ----------
            *arg :
                The first argument is assumed to be the queue for the parallel processing defined in the parent, 
                and it is assigned to self.queue and self.par is set to True. 
        
        '''
        if len(arg)>0:
            self.par=True      #flag for parallel processing
            self.queue=arg[0]  #multiprocessing.queue as the first argument
        if self.model=='py':
            self.main()
        else: 
          if self.model=='spectre':
              # Saving the analog waveform of the input as well
              self.IOS.Members['A_OUT']= IO()
              _=spice_iofile(self, name='A_OUT', dir='out', iotype='event', sourcetype='v', datatype='complex', ionames=['inniputti', 'outtiputti'])
              #self.preserve_iofiles = True
              #self.preserve_spicefiles = True
              #self.interactive_spice = True
              self.nproc = 1
              self.spiceoptions = {
                          'eps': '1e-6'
                      }
              self.spiceparameters = {
                          'Capval': str(self.Capval),
                          'rval': str(self.Rval)
                      }
              
              self.spicecorner = {
                          'corner': 'top_tt',
                          'temp': 27,
                      }
              self.spicemisc.append('Vinniputti inniputti  gnd vsource mag=1') 
              # Example of defining supplies (not used here because the example filter has no supplies)
              #_=spice_dcsource(self,name='dd',value=self.vdd,pos='VDD',neg='VSS',extract=True,ext_start=2e-9)
              _=spice_dcsource(self,name='gnd',value=0,pos='gnd',neg='0')

              # Simulation command
              _=spice_simcmd(self,sim='ac')
              self.run_spice()

          if self.par:
              self.queue.put(self.IOS.Members[Z].Data)


if __name__=="__main__":
    import matplotlib.pyplot as plt
    from  filter import *
    from  filter.controller import controller as filter_controller
    import pdb

    models=[ 'spectre' ]
    duts=[]
    for model in models:
        d=filter()
        duts.append(d) 
        d.model=model
        #d.preserve_iofiles=True
        #d.preserve_spicefiles=True
        #d.interactive_rtl=True
        #d.interactive_spice=True
        d.init()
        d.run()

    for k in range(len(duts)):
        hfont = {'fontname':'Sans'}
        if duts[k].model == 'eldo' or duts[k].model=='spectre':
            figure,axes = plt.subplots(2,1,sharex=True)
            axes[0].plot(duts[k].IOS.Members['A_OUT'].Data[:,0].real,
                    20*np.log10(np.abs(duts[k].IOS.Members['A_OUT'].Data[:,1])),label='Input')
            axes[1].plot(duts[k].IOS.Members['A_OUT'].Data[:,0].real,
                    20*np.log10(np.abs(duts[k].IOS.Members['A_OUT'].Data[:,2])),label='Output')
            axes[0].set_xscale('log')
            axes[1].set_xscale('log')
            axes[0].set_ylabel('Input', **hfont,fontsize=18);
            axes[1].set_ylabel('Output', **hfont,fontsize=18);
            axes[1].set_xlabel('Time (s)', **hfont,fontsize=18);
            #axes[0].set_xlim(0,11/rs)
            #axes[1].set_xlim(0,11/rs)
            axes[0].grid(True)
            axes[1].grid(True)
        else:
            pass
        titlestr = "Filter model %s" %(duts[k].model) 
        plt.suptitle(titlestr,fontsize=20);
        plt.grid(True);
        printstr="./inv_%s.eps" %(duts[k].model)
        plt.show(block=False);
        figure.savefig(printstr, format='eps', dpi=300);
    input()
