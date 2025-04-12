Ext._define('rh.dayoff.usufruct.ConflictsWindow', {
    extend: 'Ext.Window',

    width: 800,

    height: 500,

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Conflitos',
                closable: true,
            }
        );
        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'fit',
                items: [
                    this.getFormPanel(cfg)
                ],
                buttons: [
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        rh.dayoff.usufruct.ConflictsWindow.superclass.constructor.call(this, cfg);
    },

    getConflictsGrid: function (cfg) {
        if (!this._conflicts)
            this._conflicts = Ext._create('rh.dayoff.usufruct.ConflictsGrid', {
                region: 'center',
                gridAutoLoad: false,
                split: true,
                frame: true,
                height: 360,
                usufruct: cfg.usufruct
            });

        return this._conflicts;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        fieldLabel: 'Servidor',
                        xtype: 'displayfield',
                        value: cfg.usufruct.employee_unicode
                    },
                    {
                        fieldLabel: 'Parcela Analisada',
                        xtype: 'displayfield',
                        value: cfg.usufruct.unicode
                    },
                    {
                        xtype: 'displayfield',
                        hideLabel: true,
                        value: 'Verifique o quadro abaixo para saber se existe(m) conflito(s).'
                    },
                    this.getConflictsGrid(cfg)
                ]

            });
        return this._formPanel;
    }
});
