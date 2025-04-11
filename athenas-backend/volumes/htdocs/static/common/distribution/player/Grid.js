Ext._define('common.distribution.player.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.distribution.player.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'search', '->', 'filter', 'download'],

    keywordFieldMessage: 'Título',

    getAllPlayersMenuCheckItem: function () {
        if (!this._allPlayersMenuCheckItem) {
            this._allPlayersMenuCheckItem = Ext._create('Ext.menu.CheckItem', {
                text: 'Listar todos',
                scope: this,
                group: 'player',
                checked: false
            });

            this._allPlayersMenuCheckItem.on({
                scope: this,
                click: function () {
                    if (this.getParams().distribution !== undefined) {
                        this.removeFilterProperty('active', 200, false);
                        this.setFilterProperty('distribution', this.getParams().distribution, 100);
                    } else {
                        console.error('O parâmetro distribution não foi passado para o grid.');
                    }
                }
            });
        }
        return this._allPlayersMenuCheckItem;
    },

    getOnlyActiveMenuCheckItem: function () {
        if (!this._onlyActiveMenuCheckItem) {
            this._onlyActiveMenuCheckItem = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente os ativos',
                scope: this,
                group: 'player',
                checked: true
            });

            this._onlyActiveMenuCheckItem.on({
                scope: this,
                click: function () {
                    if (this.getParams().distribution !== undefined) {
                        this.setFilterProperty('active', true, 200);
                        this.setFilterProperty('distribution', this.getParams().distribution, 100);
                    } else {
                        console.error('O parâmetro distribution não foi passado para o grid.');
                    }
                }
            });
        }
        return this._onlyActiveMenuCheckItem;
    },

    getOnlyInactiveMenuCheckItem: function () {
        if (!this._onlyInactiveMenuCheckItem) {
            this._onlyInactiveMenuCheckItem = Ext._create('Ext.menu.CheckItem', {
                text: 'Somente os inativos',
                scope: this,
                group: 'player',
                checked: false
            });

            this._onlyInactiveMenuCheckItem.on({
                scope: this,
                click: function () {
                    if (this.getParams().distribution !== undefined) {
                        this.setFilterProperty('active', false, 200);
                        this.setFilterProperty('distribution', this.getParams().distribution, 100);
                    } else {
                        console.error('O parâmetro distribution não foi passado para o grid.');
                    }
                }
            });
        }
        return this._onlyInactiveMenuCheckItem;
    },

    getFilterAction: function () {
        if (!this._filterAction) {
            this._filterAction = Ext._create('Ext.Button', {
                text: 'Filtros',
                iconCls: 'icon-distribution icon-dist-filter',
                menu: [
                    this.getAllPlayersMenuCheckItem(),
                    this.getOnlyActiveMenuCheckItem(),
                    this.getOnlyInactiveMenuCheckItem()
                ]
            });
        }
        return this._filterAction;
    },

    getColumnModel: function () {
        if (!this._columnModel) {
            var dateRenderer = Ext.util.Format.dateRenderer('d/m/Y H:i');

            this._columnModel = Ext._create('Ext.grid.ColumnModel', [
                Ext._create('Ext.grid.RowNumberer'),
                { header: 'Cod.', dataIndex: 'pk', width: 50, hidden: true },
                { header: 'Descrição',   dataIndex: 'unicode', hidden: true, id: 'autoExpandColumn' },
                { header: 'Título', dataIndex: 'title', width: 250 },
                { header: 'Ativo', dataIndex: 'active', width: 75, hidden: false, renderer: function (value) { return (value ? 'SIM' : 'NÃO'); } },
                { header: 'Distribuição', dataIndex: 'distribution_unicode', width: 120, hidden: true },
                { header: 'Modificado em', dataIndex: 'modified_at', width: 90, renderer: dateRenderer, hidden: true },
                { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 120, hidden: true },
                { header: 'Criado em', dataIndex: 'created_at', width: 90, renderer: dateRenderer, hidden: true },
                { header: 'Criado por', dataIndex: 'created_by_unicode', width: 120, hidden: true }
            ]);
        }

        return this._columnModel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            keywordFieldWidth: 200
        });

        common.distribution.player.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'common.distribution.player.Restful',
    'common.distribution.player.Grid'
);
