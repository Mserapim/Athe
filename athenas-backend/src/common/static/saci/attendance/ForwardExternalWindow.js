Ext._define('common.saci.attendance.ForwardExternalWindow', {
    extend: 'Ext.Window',

    getDestinationField: function() {
        if(!this._destinationField){
            this._destinationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Órgão externo",
                allowBlank: false,
                rest: "rh.generalorgan.Restful",
                name: "destination",
                disabled: false,
                preFilter: [
                    {property: 'lotacao', value: null, stage: 100}
                ]
            });

        }
        return this._destinationField;
    },

    getFeedbackPanel: function(cfg) {
        if(!this._feedbackPanel)
            this._feedbackPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Parecer',
                border: true,
                frame: false,
                scope: this,
                items: [
                    {
                        allowBlank: false,
                        fieldLabel: "Relato",
                        name: "feedback",
                        xtype: "ckeditor",
                        hideLabel: true,
                        height: 240,
                        submit: true,
                    }
                ]
            });
        return this._feedbackPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getDestinationField(),
                    this.getFeedbackPanel()
                ]
            });

        return this._formPanel;
    },

    finalize: function() {
        var rest = Ext._create('common.saci.attendance.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Gerendo termo de encaminhamento...'});
        var values = this.getFormPanel().getForm().getValues();

        values.competence_others = 'on';

        values.destination = isNaN(parseInt(values.destination)) ? undefined : values.destination;

        if(values.destination === undefined) {
            Ext.Msg.show({
                title: 'Encaminhamento Externo',
                msg: "Informe o Órgão de destino do encaminhamento.",
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });

        } else {
            mask.show();
            rest.finalize(
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
                                title: 'Encaminhamento Externo',
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
                            title: 'Encaminhamento Externo',
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
        }

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Encaminhamento Externo'
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
                    handler: function() { this.finalize(); }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        common.saci.attendance.ForwardExternalWindow.superclass.constructor.call(this, cfg);
    }
});
