Ext._define('rh.gfp.paycheckdifference.CorrectionFactorGrid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gfp.paycheckdifference.CorrectionFactorRestful',

    restWindow: 'rh.gfp.paycheckdifference.CorrectionFactorWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'loadFile', '-', 'search', 'clean', '->', 'download'],

    getConfigActionsItems: function(cfg){
        var menu = rh.gfp.paycheckdifference.CorrectionFactorGrid.superclass.getConfigActionsItems.call(this, cfg);
        menu['loadFile'] = {
            text: 'Carregar arquivo XLS',
            iconCls: 'icon-fopag icon-arrow-repeat',
            scope: this,
            handler: this.loadFile
        };
        
        return menu;
    },

    loadFile: function(){
        new rh.gfp.paycheckdifference.CorrectionFactorLoaderWindow({
            success: {
                scope: this,
                callback: function() { this.getStore().reload() }
            }                
        }).show();
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Identificador', dataIndex: 'identifier', id: 'autoExpandColumn'},
                    {header: 'Fator', dataIndex: 'factor', width: 90},
                    {header: 'Ref. Pag. Ano', dataIndex: 'ref_payment_year', width: 70},
                    {header: 'Ref. Pag. Mês', dataIndex: 'ref_payment_month', width: 70},
                    {header: 'Ref. Dif. Ano', dataIndex: 'ref_difference_year', width: 90},
                    {header: 'Ref. Dif. Mês', dataIndex: 'ref_difference_month', width: 90},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 120},
                    {header: 'Cirado em', dataIndex: 'created_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120},
                    {header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.gfp.paycheckdifference.CorrectionFactorRestful',
    'rh.gfp.paycheckdifference.CorrectionFactorGrid'
);

