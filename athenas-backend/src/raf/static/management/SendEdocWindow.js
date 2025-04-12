
Ext._define('raf.management.SendEdocWindow', {
    extend: 'Ext.Window',

    isEmpty: function(content) {
        let regex = /(<([^>]+)>)/ig;
        if(content.replace(regex, ""))
            return false
        return true
    },

    getEditor: function (cfg) {
        if (!this._ckeditoField) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {
                allowBlank: true,
                hideLabel: true,
                startupFocus: false,
                editorConfig: {
                    forcePasteAsPlainText: true
                },
            });
            this._ckeditoField = Ext._create('toolkit.fields.CKEditor', cfg);
        }
        return this._ckeditoField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                hideLabel: true,
                items: [
                    this.getEditor({
                        name: 'content',
                        width: 900,
                        height: 385
                    })
                ]
        });
        return this._formPanel;
    },

    send: function() {

        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Enviando E-Doc...'});
        
        if (!this.isEmpty(values.content)) {
            
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RAFFunctionalActivityReport', 'send_edoc'),
                callback: function() {
                    this.managementGroupGrid.getStore().reload();
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Eviar E-Doc',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.close();
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Eviar E-Doc',
                        msg: 'Falha na solicitação',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    month: this.params.month,
                    year: this.params.year,
                    content: values.content
                },
            });
        } else {
            Ext.Msg.show({
              title: 'Enviar E-Doc',
              msg: 'Conteúdo do documento encontra-se vazio. Digite o documento.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Enviar',
                    scope: this,
                    handler: function() { this.send(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Comunicar via E-doc',
                modal: true,
                resizable: false,
                border: false,
                width: 900,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        raf.management.SendEdocWindow.superclass.constructor.call(this, cfg);
    }
});
