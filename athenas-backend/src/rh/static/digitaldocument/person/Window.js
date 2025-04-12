
Ext._define('rh.digitaldocument.person.Window', {
    extend: 'rh.digitaldocument.Window',
    rest: 'rh.digitaldocument.attachment.Restful',

    constructor: function(cfg) {
        cfg = cfg || {};
        rh.digitaldocument.Window.superclass.constructor.call(this, cfg);
        this._observe();
    },

    _observe: function() {
        var values = this.getParams();
        if(values != undefined && values.person != undefined){
            this.getPersonField().setReadOnly(true);
        }
    },

    resetForm: function() {
        this.getFormPanel().items.each(
            (field)=> {
                if(field.name != 'person'){
                    field.reset();
                }
            }, 
        this);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getPersonField(),
                    {
                        maxLength: 260,
                        allowBlank: false,
                        fieldLabel: "Nome",
                        name: "name",
                        xtype: "textfield",
                        width: 400
                    },
                    {
                        xtype: 'ged-fileuploadfield',
                        fieldLabel: 'Arquivo',
                        allowBlank: true,
                        name: 'file',
                        hiddenName: 'file',
                        value: cfg.values.file,
                        listeners: {
                            scope: this,
                            afterchange: function(field, value, oldVal)
                            {
                                var titleField = this.find('name', 'name')[0],
                                    filename = value.split('/').pop();

                                titleField.setValue(filename);
                                titleField.focus();
                            }
                        }
                    }
                ]
            });
        return this._formPanel;
    },
});
