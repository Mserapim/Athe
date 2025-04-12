Ext._define('rh.registration.forminformation.admin.WindowMessageValidation', {
    extend: 'Ext.Window',

    constructor: function (cfg) {
        var title_window = 'Mensagem de validação';
        var text_button = 'Validar/Enviar Mensagem';

        cfg = (cfg ? cfg : {});

        if (cfg.type_send == 'CONFIRMATION') {
            title_window = 'Retorno de tentativa de Validação';
            text_button = 'Confirmar validação/notificação';
        }

        Ext.apply(
            cfg,
            {
                title: title_window,
                width: 600,
                height: 500,
                modal: true,
                resizable: false,
                border: false,
                scope: this,
                buttons: [
                    {
                        text: text_button,
                        scope: this,
                        handler: function () {
                            if (cfg.type_send == 'CONFIRMATION')
                                cfg.data_send.confirm_validation = true;
                            cfg.father.perform_validation(cfg.data_send, this._textMessageNotification.getValue());
                            this.destroy();
                        }
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function () {
                            this.destroy();
                        }
                    }
                ],
                items: this.getTextForm(cfg),
            }
        );
        rh.registration.forminformation.admin.WindowMessageValidation.superclass.constructor.call(this, cfg);
    },

    getTextForm: function (cfg) {
        if (this._textForm == undefined){
            this._textForm = Ext._create('Ext.form.FormPanel', {
                frame: true,
                height: 430,
                items: [this.getTextMessageNotification(cfg)]
            });
            this.getTextDependents(cfg.data_send);

        }else{
            // this.getTextMessageNotification().setValue(cfg.data_send['text']);
            this.getTextDependents(cfg.data_send);            
        }
        if (cfg.data_send['message_err'] != '' && cfg.data_send['message_err'] != undefined)
            this._textForm.add({
                name: 'message_err',
                fieldLabel: 'Mensagem DGPFP',
                labelAlign: 'top',
                xtype: 'xhtmleditor',
                value: cfg.data_send['message_err']
            });
        return this._textForm;
    },

    getTextDependents: function (data_send) {        
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('RegistrationFormInformationAdmin', 'dependent_validation'),
            params: {
                data: JSON.stringify(data_send),
            },
            scope: this,
            success: function (request) {
               var text = Ext.decode(request.responseText).text;   
               this.getTextMessageNotification().setValue(text)
            },
            failure: function (request) {
                Ext.Msg.show({
                    title: 'Informação',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg:request.responseText
                });
            }
            
        });
    },

    getTextMessageNotification: function (cfg) {       
        if (this._textMessageNotification == undefined)
            this._textMessageNotification = Ext._create('toolkit.plugins.XHtmlTextEditor', {
                name: 'text',
                fieldLabel: 'Mensagem de notificação',
                labelAlign: 'top',
                xtype: 'xhtmleditor',
                height: 410,
                width: 450,
                value: cfg.data_send['text']
            });
        return this._textMessageNotification;
    },
});
