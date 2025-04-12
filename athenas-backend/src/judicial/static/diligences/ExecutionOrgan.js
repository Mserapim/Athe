/**
 *
 **/
 Ext._define('judicial.diligences.ExecutionOrgan', {

    extend: 'Ext.Panel',

    mixins: {'deliveryAttemptPanel': 'judicial.diligences.DeliveryAttemptPanel'},

    getDiligenceGrid: function(cfg) {
    	if(!this._diligenceGrid){
            this._diligenceGrid = Ext._create('judicial.diligences.ExecutionOrganGrid', {
                title: 'Diligências',
                region: 'center',
                minWidth: 500,
                allowUpdate: false,
            	allowRemove: false,
            	columnAction: false,
                gridAutoLoad: (cfg.gridAutoLoad !== undefined ? cfg.gridAutoLoad : true),
            	hideItemsToolbar: ['add', 'remove', 'download'],
                hiddenColumns: ['deadline', 'responsible_delivering_unicode', 'icon_status', 'created_at', 'out_court_lawsuit_location_unicode']
            });
            
            this._diligenceGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
    
                    if(selection.length > 0)
                        this.diligence(selection[0].get('pk'));
                    else
                        this.diligence(null);
                }
            });
        }
    
    
        return this._diligenceGrid;
    },

    constructor: function(cfg) {
        cfg = this.configurePanel(cfg);
        
        judicial.diligences.ExecutionOrgan.superclass.constructor.call(this, cfg);
        
        this.getDiligenceGrid().getStore().on({
            clear: function(store) { store.isLoaded = false },
            beforeload: function(store) { store.isLoaded = true }
        });
        
        this.on({
            scope: this,
            activate: function() {
                var vm = this;
                setTimeout(
                    function () {
                        if (!vm.getDiligenceGrid().getStore().isLoaded)
                            vm.getDiligenceGrid().getStore().reload();
                    }, 
                    500
                );
            }
        })
    }


});
