Ext._define('standard.emailtemplate.Window', {
    extend: 'core.RestfulWindow',

    rest: 'standard.emailtemplate.Restful',

    width:700,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        tabPosition: 'top',
                        border: false,
                        items: [
                            this.getTabMainInfo(cfg),
                            this.getTabExtraInfo(cfg),
                        ]
                    })
                ]
            });

        return this._formPanel;
    },

    getTabMainInfo: function (cfg) {
        if (!this._tabMainInfo)
            this._tabMainInfo = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Principal',
                border: false,
                frame: true,
                scope: this,
                height: 550,
                items: this._getMainInfo(cfg)
            });
        return this._tabMainInfo;
    },

    getTabExtraInfo: function (cfg) {
        if (!this._tabExtraInfo)
            this._tabExtraInfo = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Informações',
                border: false,
                frame: true,
                scope: this,
                height: 550,
                items: this._getExtraInfo(cfg)
            });
        return this._tabExtraInfo;
    },

    _getMainInfo: function() {
        return [
            {
                name: "code",
                fieldLabel: "Código",
                xtype: "textfield",
                allowBlank: false,
                maxLength: 150,
                width: 450
            },
            {
                name: "subject",
                fieldLabel: "Assunto",
                xtype: "textfield",
                allowBlank: false,
                maxLength: 150,
                width: 450
            },
            {
                name: "contents",
                fieldLabel: "Conteúdo",
                allowBlank: true,
                height: 350,
                xtype: "ckeditor",
                toolbarGroups: [
                    {name: 'styles', itens: ['Format']},
                    {name: 'clipboard'},
                    {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                    {
                        name: 'paragraph',
                        groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                    },
                ],
            }
        ]
    },

    _getExtraInfo: function() {
        return [
            {
                xtype: 'container',
                items: [
                    {
                        name: "description",
                        fieldLabel: "Descrição",
                        allowBlank: true,
                        height: 400,
                        xtype: "ckeditor",
                        toolbarGroups: [
                            {name: 'styles', itens: ['Format']},
                            {name: 'clipboard'},
                            {name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ]},
                            {
                                name: 'paragraph',
                                groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                            },
                        ]
                    }
                ]
            }
        ]
    },

});

