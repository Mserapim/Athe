/**
 *
 **/
Ext._define('adm.patrimonio.parametro.ContaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.parametro.ContaWindow',

    keywordFieldMessage: 'Título',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 60, hidden: true},
                    {header: 'Título', dataIndex: 'titulo', id: 'autoExpandColumn'},
                    {header: 'Prefixo', dataIndex: 'prefix', width: 60},
                    {header: 'Sufixo', dataIndex: 'sufix', width: 60},
                    {header: 'Tipo', dataIndex: 'tipo_display', width: 120},
                    {header: 'Sequência', dataIndex: 'sequencia_unicode', width: 145},
                    {
                        header: 'Principal',
                        dataIndex: 'principal',
                        width: 60,
                        renderer: function(value) { return value ? 'SIM' : 'NÃO'; }
                    }
                ]
            );

        return this._columnModel;
    },

    changeFitlerTipo: function(tipo) {
        if(tipo) {
            this.setFilterProperty('tipo', tipo, 0);
        }
        else
            this.removeFilterProperty('tipo', 0);
    },

    changeFilterPrincipal: function(enable) {
        if(enable)
            this.setFilterProperty('principal', true, 1);
        else
            this.removeFilterProperty('principal', 1);
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Somente o principal',
                    checked: false,
                    listeners: {
                        scope: this,
                        checkchange: function(menu, checked) {
                            this.changeFilterPrincipal(checked);
                        }
                    }
                },
                '-',
                {
                    text: 'Controlado',
                    group: 'tipo',
                    checked: false,
                    scope: this,
                    handler: function() { this.changeFitlerTipo(1); }
                },
                {
                    text: 'Relacionado',
                    group: 'tipo',
                    checked: false,
                    scope: this,
                    handler: function() { this.changeFitlerTipo(2); }
                },
                {
                    text: 'Todas',
                    group: 'tipo',
                    checked: true,
                    scope: this,
                    handler: function() { this.changeFitlerTipo(undefined); }
                }
            ];

        return this._filterMenu;
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.parametro.ContaRestful',
    'adm.patrimonio.parametro.ContaGrid'
);
