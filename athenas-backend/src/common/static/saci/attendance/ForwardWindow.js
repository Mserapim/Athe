Ext._define('common.saci.attendance.ForwardWindow', {
    extend: 'Ext.Window',

    width: 800,

    getDestinationField: function(){
        if(!this._destinationField){
            this._destinationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Encaminhar para",
                allowBlank: false,
                rest: "rh.generalorgan.Restful",
                name: "destination",
                disabled: false,
                preFilter: [
                    {property: 'habilita_protocolo', value: true, stage: 100},
                    {property: 'lotacao', value: null, stage: -100}
                ]
            });

        }
        return this._destinationField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getDestinationField(),
                    this.getJustificationPanel()
                ]
            });

        return this._formPanel;
    },

    getJustificationPanel: function(cfg) {
        if(!this._justificationPanel)
            this._justificationPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Justificativa',
                border: true,
                frame: false,
                scope: this,
                items: [
                    {
                        allowBlank: false,
                        fieldLabel: "Justificativa",
                        name: "justification",
                        xtype: "ckeditor",
                        hideLabel: true,
                        height: 250,
                        submit: true,
                    }
                ]
            });
        return this._justificationPanel;
    },

    forward: function() {
        var rest = Ext._create('common.saci.attendance.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'encaminhando...'});
        var values = this.getFormPanel().getForm().getValues();

        values.destination = isNaN(parseInt(values.destination)) ? undefined : values.destination
        mask.show();
        rest.movement(
            this.oId,
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Encaminhando',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Encaminhamento',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
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


        common.saci.attendance.ForwardWindow.superclass.constructor.call(this, cfg);
    }
});
