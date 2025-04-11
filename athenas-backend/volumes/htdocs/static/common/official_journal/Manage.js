/**
 *
 **/

Ext._define('common.official_journal.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
        {
            this._grid = Ext._create('common.official_journal.JournalGrid', {
                region: 'center'
            });

            var supGrid = this.getSuplementGrid();
            this._grid.on('rowclick', function(grid, index){
                var record = grid.getStore().getAt(index);
                supGrid.enable();
                supGrid.setParam('journal', record.get('pk'))
                supGrid.setFilterProperty('journal_id', record.get('pk'), 100, true);
            });
        }

        return this._grid;
    },

    getSuplementGrid: function()
    {
        if(!this._suplementsGrid)
            this._suplementsGrid = Ext._create('common.official_journal.JournalSuplementGrid', {
                region: 'south',
                height: 250,
                disabled: true,
                gridAutoLoad: false
            });

        return this._suplementsGrid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Diários Oficiais',
            layout: 'border',
            items: [this.getGrid(), this.getSuplementGrid()]
        });

        common.official_journal.Manage.superclass.constructor.call(this, cfg);
    }
});
