/**
 *
 **/
Ext._define('judicial.diligences.officer.FactoryDiligenceGridMixin', {
    factoryDiligenceGrid: function(config) {

        Ext.applyIf(config.gridConfig, {
            allowCreate: false,
            allowRemove: false,
            allowUpdate: false,
        });

        var grid = Ext._create(
            'judicial.diligences.JudicialDiligenceOfficerGrid', 
            config.gridConfig
        );

        grid.setFilter(config.filters || []);

        grid.getSelectionModel().on({
            scope: this,
            selectionchange: function(sm) {
                var selection = sm.getSelections();

                if(selection.length > 0)
                    config.selection(selection[0]);
                else
                    config.selection(null);
            }
        });

        grid.getStore().on({
            scope:this,
            load: function(store) {
                core.invokeCallback((config.loadCallback || {fn: Ext.emptyFn}), store);
            }
        });

        return grid;
    }
});