/**
 *
 **/
Ext._define('adm.patrimonio.DocumentoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.DocumentoRestfulWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 30,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {header: 'Título', dataIndex: 'titulo', id: 'autoExpandColumn'},
                    {
                        header: 'Por',
                        dataIndex: 'criado_por',
                        width: 100,
                    },
                    {
                        header: 'Em',
                        dataIndex: 'criado',
                        width: 105,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')
                    },
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            adm.patrimonio.DocumentoGrid.superclass.getToolbar.call(this, cfg);

            this._toolbar.remove(10);
            this._toolbar.remove(9);
            this._toolbar.remove(8);
            this._toolbar.remove(7);
            this._toolbar.remove(6);
            this._toolbar.remove(5);
            this._toolbar.remove(4);
        }

        return this._toolbar;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        cfg.columnAction = false;

        adm.patrimonio.DocumentoGrid.superclass.constructor.call(this, cfg);
    }
});
