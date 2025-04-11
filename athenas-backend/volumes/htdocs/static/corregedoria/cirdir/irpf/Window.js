Ext._define('corregedoria.cirdir.irpf.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.irpf.Restful',

    width: 750,

    getChoiceType: function() {
        if(!this._choiceType) {
            this._choiceType = Ext._create("standard.fields.ChoiceField",{
                fieldLabel: 'Tipo',
                hiddenName: 'of_who',
                width: 105,
                choiceId: 'cirdir.KIND',
            });
        }
        return this._choiceType;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                    width: 615
                },
                items: [
                    {
                        allowBlank: false,
                        fieldLabel: "Anexo",
                        xtype: "ged-fileuploadfield",
                        name: "file"
                    },
                    this.getChoiceType(),
                ]
            });

        return this._formPanel;
    },

    _afterConstructor: function() {        
        let created = (this.initialConfig || {}).oId === undefined;
        let employee = (this.params || {}).employee_type == "S";
        
        if(created) {
            this.getChoiceType().setValue(1);
            if(employee) {
                this.getChoiceType().disable();
            }
        } else {
            if(employee) {
                this.getChoiceType().disable();
            }
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        
        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
        });
        
        corregedoria.cirdir.irpf.Window.superclass.constructor.call(this, cfg);
        this._afterConstructor();
    },

});
