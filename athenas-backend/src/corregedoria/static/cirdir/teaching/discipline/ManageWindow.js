Ext._define('corregedoria.cirdir.teaching.discipline.ManageWindow', {
    extend: 'Ext.Window',

    width: 900,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    this.getGrid(cfg)
                ]
            });

        return this._formPanel;
    },

    getGrid: function(cfg) {
        if(!this._grid)
            this._grid = Ext._create('corregedoria.cirdir.teaching.discipline.Grid', {
                height: 800
            });
        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                resizable: false,
                border: false
            }
        );

        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(cfg),
                buttons: [
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        corregedoria.cirdir.teaching.discipline.ManageWindow.superclass.constructor.call(this, cfg);
    }
});
