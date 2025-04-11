/**
 *
 **/
Ext._define('common.siatu.servico.AtendentesGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.servico.AtendentesWindow',

    keywordFieldMessage: 'Atendente',

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = common.siatu.servico.AtendentesGrid.superclass.getToolbar.call(this, cfg);

            this.getKeywordField().setWidth(280);

            this._toolbar.remove(this._toolbar.getComponent(0)); // Adicionar
            this._toolbar.remove(this._toolbar.getComponent(0)); // Editar
            this._toolbar.remove(this._toolbar.getComponent(0)); // Remover
            this._toolbar.remove(this._toolbar.getComponent(0)); // Separador
            this._toolbar.remove(this._toolbar.getComponent(6)); // Download
        }

        return this._toolbar;
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                width: 65,
                scope: this,
                items: [
                    {
                        iconCls: 'icon-16px icon-core icon-core-delete',
                        tooltip: 'Remover item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            record && this.removeItems(record);
                        }
                    }
                ]
            });

        return this._actionColumn;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'busy', width: 20, renderer: common.siatu.rendererIconGrid},
                    {header: 'Usuario', dataIndex: 'username', width: 100},
                    {header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn'},
                    {header: '', dataIndex: 'icon_dist', width: 25, renderer: common.siatu.rendererIconGrid},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
            }
        );

        Ext.apply(
            cfg,
            {
                allowUpdate: false
            }
        );

        common.siatu.servico.AtendentesGrid.superclass.constructor.call(this, cfg);
    }
});