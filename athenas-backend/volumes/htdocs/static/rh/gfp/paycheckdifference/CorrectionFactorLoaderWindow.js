Ext._define('rh.gfp.paycheckdifference.CorrectionFactorLoaderWindow', {
    extend: 'Ext.Window',
    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = new Ext.form.FormPanel({
                border: false,
                frame: true,
                scope: this,
                items:[
                    {
                        fieldLabel: 'Arquivo de correções XLS',
                        xtype: 'ged-fileuploadfield',
                        name: 'correctionfile',
                        allowBlank: true,
                        width: 260,
                        listeners: {
                            scope: this,
                            afterchange: function(field, value, oldVal) {
                                let filename = value.split('.').pop();
                                let displayerrorField = this.getFormPanel().getForm().findField('displayerror');
                                if(!['xls', 'xlsx'].includes(filename)){
                                    displayerrorField.setValue('* Permitido apenas arquivos XLS');
                                } else {
                                    displayerrorField.setValue('');
                                }
                            }
                        }
                    },
                    {
                        maxLength: 4,
                        allowBlank: true,
                        fieldLabel: "Importar apartir do ano",
                        name: "startyear",
                        value: "2000",
                        xtype: "numberfield",
                        width: 260,
                    },
                    {
                        width: 260,
                        maxLength: 2,
                        allowBlank: false,
                        fieldLabel: "Mês de referência do arquivo",
                        name: "month",
                        xtype: "numberfield",
                    },
                    {
                        width: 260,
                        maxLength: 4,
                        allowBlank: false,
                        fieldLabel: "Ano de referência do arquivo",
                        name: "year",
                        xtype: "numberfield",
                    },
                    {
                        width: 260,
                        maxLength: 4,
                        allowBlank: false,
                        name: "displayerror",
                        xtype: "displayfield",
                    }

                ],
                buttons: [
                    {
                        text: 'Aplicar',
                        scope: this,
                        handler: this.doSubmit
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]                

            });
    
        return this._formPanel;
    },

    doSubmit: function(){
        var form = this.getFormPanel().getForm();

        form.waitMsgTarget = this.getEl();
        form.submit({
            url: toolkit.util.Normalize.controller_action('GFPEntryDifference', 'load_file'),
            scope: this,
            waitMsg: 'Carregando arquivo...',
            success: function(form, action) {
                var fn = this.success;
                fn && fn.callback.call(fn.scope ? fn.scope : window);
                this.destroy();
            },
            failure: function(form, action) {
                if(action.failureType == 'client')
                    message = 'Erro de comunicação com servidor, tente novamente mais tarde.'
                else
                    message = action.result.message;

                Ext.Msg.show({
                    title: this.title,
                    msg: message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });

                this.failure && this.failure.callback.call(this.failure.scope ? this.failure.scope : window);
            }
        });
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(cfg, {
            title: 'Carregar arquivo',
            modal: true,
            resizable: false,
            width: 400,
            items: this.getFormPanel()
        });

        rh.gfp.paycheckdifference.CorrectionFactorLoaderWindow.superclass.constructor.call(this, cfg);
    }
});