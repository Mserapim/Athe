/**
 *
 **/
Ext._define('common.siatu.chamado.anexo.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.anexo.Restful',

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if(!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    handler: this.save,
                    handler: function() { this.save(true) }
                }].concat(this._buttons);

            if(cfg.action == 'create' && !cfg.disableSaveAndNew)
                this._buttons = [{
                    text: 'Salvar e novo',
                    scope: this,
                    handler: function() { this.save(false) }
                }].concat(this._buttons);
        }

        return this._buttons;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                        {
                            fieldLabel: 'Arquivo',
                            name: 'arquivo',
                            hiddenName: 'arquivo',
                            xtype: 'ged-fileuploadfield'
                        }
                ]
            });

        return this._formPanel;
    }
});
