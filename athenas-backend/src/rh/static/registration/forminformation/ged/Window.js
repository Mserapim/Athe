/**
 *
 */

Ext._define('rh.registration.forminformation.ged.Window', {
    extend: 'Ext.Window',

    getParams: function() {
        var params = {};
        Ext.apply(params, this.params);
        return params;
    },

    removeItems: function(el) {
        var mask = new Ext.LoadMask(el, {
            msg: 'Removendo os itens selecionados...'
        });

        mask.show();
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('RegistrationFormInformation', 'remove_attachment'),
            params: this.getParams(),
            method: 'POST',
            scope: this,
            callback: function() {
                var success = this.success;
                mask.hide();
                delete mask;
                success && success.callback && success.callback.call(success.scope ? success.scope : window);
            },
            success: function(request) {
                var obj = Ext.decode(request.responseText);

                if(!obj.success)
                    Ext.Msg.show({
                        title: this.title,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: obj.message
                    });
            },
            failure: function(request) {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            }
        });
    },

    save: function(close) {
        var form = this.getFormPanel().getForm();

        form.waitMsgTarget = this.getEl();
        form.submit({
            url: toolkit.util.Normalize.controller_action('RegistrationFormInformation', this.action + '_attachment'),
            params: this.getParams(),
            scope: this,
            waitMsg: 'Salvando informações...',
            success: function(form, action) {
                var success = this.success;
                success && success.callback && success.callback.call(success.scope ? success.scope : window);
                if(this.close) this.destroy();
                else {
                    this.getFormPanel().getForm().reset();
                }
            },
            failure: function(form, action) {
                var message = '';
                var failure = this.failure;

                failure && failure.callback && failure.callback.call(failure.scope ? failure.scope : window);

                if(action.failureType == 'connect')
                    message = 'Recurso indisponivel no momento, tente novamente mais tarde.'
                else
                    message = action.result.message

                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        });
    },

    getFormPanel: function() {
        if(!this._formPanel){
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                    width: 400
                },
                items: [
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo de Documento',
                        hiddenName: 'document_type',
                        choiceId: 'rh.DIGITAL_DOCUMENT_TYPE',
                    },
                    {
                        fieldLabel: 'Arquivo',
                        name: 'file',
                        hiddenName: 'file',
                        xtype: 'ged-fileuploadfield'
                    }
                ],
                buttons: [
                    {
                        text: 'Salvar e novo',
                        scope: this,
                        handler: function() { this.save(false) }
                    },
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: function() { this.save(true) }
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            });
        }
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            title: 'Anexo',
            modal: true,
            resizable: false,
            width: 550,
            items: this.getFormPanel()
        });

        rh.registration.forminformation.ged.Window.superclass.constructor.call(this, cfg);

        this.values && this.getFormPanel().getForm().setValues(this.values);
    }
});