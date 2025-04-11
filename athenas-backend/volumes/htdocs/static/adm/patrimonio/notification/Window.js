Ext._define('adm.patrimony.notification.Window', {
    extend: 'core.RestfulWindow',
    rest: 'adm.patrimony.notification.Restful',

    width: 900,

    doValidation: function() {
        var values = this.getFormPanel().getForm().getValues();

        if (!values.content)
            throw "Por favor, informe o conteúdo da notificação.";
    },

    save: function(close) {
        try {
            this.doValidation();
            adm.patrimony.notification.Window.superclass.save.call(this, close);
        } catch (e) {
            Ext.Msg.show({
                title: 'Validação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: e
            });
        }
    },

    getDisplayFieldPanel: function () {
        if (this._displayPanel) {
            return this._displayPanel;
        }

        this._displayPanel = Ext._create('Ext.Panel', {
            layout: 'form',
            frame: true,
            defaults: {
                style: {
                    backgroundColor: '#ccd8e7',
                    border: '1px solid #99bbe8',
                    padding: '2px',
                    height: '15px'
                }
            },
            items: [
                {
                    xtype: 'displayfield',
                    fieldLabel: 'Destinatário',
                    name: 'destination_unicode'
                },
                {
                    xtype: 'displayfield',
                    fieldLabel: 'Protocolo',
                    name: 'protocol_unicode'
                },
            ]
        });

        return this._displayPanel;
    },

    getContentPanel: function () {
        if (this._contentPanel) {
            return this._contentPanel;
        }

        this._contentPanel = Ext._create('Ext.Panel', {
            layout: 'form',
            labelAlign: 'top',
            frame: true,
            items: [
                {
                    xtype: 'ckeditor',
                    fieldLabel: 'Conteúdo',
                    name: 'content',
                    height: 242,
                    startupFocus: true,
                }
            ]
        });

        return this._contentPanel;
    },

    getFormPanel: function () {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: false,
                border: false,
                labelWidth: 85,
                items: [
                    this.getDisplayFieldPanel(),
                    this.getContentPanel(),
                ]
            });
        }
        return this._formPanel;
    }

});
