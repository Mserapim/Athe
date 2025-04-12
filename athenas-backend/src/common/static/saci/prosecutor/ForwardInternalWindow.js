Ext._define('common.saci.prosecutor.ForwardInternalWindow', {
    extend: 'common.saci.attendance.ForwardWindow',

    getEmployeeField: function(cfg) {
       if(!this._employeeField){
           this._employeeField = Ext._create('core.fields.ComboField', {
               fieldLabel: 'Atendido por',
               hiddenName: 'employee',
               displayField: 'description',
               store: Ext._create('Ext.data.Store', {
                   baseParams: {
                       department: 0
                   },
                   proxy: Ext._create('Ext.data.HttpProxy', {
                       url: core.callAction('SACIStepRestful', 'prosecutor_location')
                   }),
                   reader: Ext._create('Ext.data.JsonReader', {
                       totalProperty: 'count',
                       root: 'collection',
                       fields: [
                           {name: 'pk', type: 'int'},
                           {name: 'description', type: 'string'},
                       ]
                   })
               }),
               width: 660,
               allowBlank: false
           });
       }

       return this._employeeField;
   },

   setValueDepartment: function(value) {

       this.getEmployeeField().getStore().setBaseParam('department', value || 0);
       this.getEmployeeField().getStore().reload();

   },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  {
                      xtype: 'hidden',
                      name: 'required_employee',
                      value: 'on'
                  },
                    this.getDestinationField(),
                    this.getEmployeeField(),
                    this.getJustificationPanel()
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Encaminhamento Interno'
        });

        Ext.apply(cfg, {
            width: 800,
            items: [
                this.getFormPanel()
            ],
            buttons: [
                {
                    text: 'Encaminhar',
                    scope: this,
                    handler: function() { this.forward(); }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });


        common.saci.prosecutor.ForwardInternalWindow.superclass.constructor.call(this, cfg);
        this.setValueDepartment(this.params.department);
    }
});
