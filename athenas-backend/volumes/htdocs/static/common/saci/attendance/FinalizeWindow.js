Ext._define('common.saci.attendance.FinalizeWindow', {
    extend: 'Ext.Window',

    width: 800,

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
                    this.getFeedbackPanel()
                ]
            });

        return this._formPanel;
    },

    finalize: function() {
        var rest = Ext._create('common.saci.attendance.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'finalizando atendimento...'});
        var values = this.getFormPanel().getForm().getValues();

        values.competence_others = 'off';

        values.destination = undefined;

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
                            title: 'Finalizando Atendimento',
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
                        title: 'Finalizando Atendimento',
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
            title: 'Finalizar atendimento'
        });

        Ext.apply(cfg, {
            width: 800,
            items: [
                this.getFormPanel()
            ],
            buttons: [
                {
                    text: 'Finalizar',
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


        common.saci.attendance.FinalizeWindow.superclass.constructor.call(this, cfg);
    }
});
