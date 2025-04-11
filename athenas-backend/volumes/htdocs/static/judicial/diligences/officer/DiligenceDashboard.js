/**
 *
 **/
 Ext._define('judicial.diligences.officer.DiligenceDashboard', {
    
    extend: 'toolkit.widget.TabPanel',

    getInDeliveryPanel: function(cfg){
        if(!this._inDeliveryPanel){
            this._inDeliveryPanel = Ext._create('judicial.diligences.officer.InDeliveryPanel', {});
        }
        return this._inDeliveryPanel;
    },

    getCancelDeliveryPanel: function(cfg){
        if(!this._cancelDeliveryPanel){
            this._cancelDeliveryPanel = Ext._create('judicial.diligences.officer.CancelDeliveryPanel', {});
        }
        return this._cancelDeliveryPanel;
    },

    getFinishedDeliveryPanel: function(cfg){
        if(!this._finishedDeliveryPanel){
            this._finishedDeliveryPanel = Ext._create('judicial.diligences.officer.FinishedDeliveryPanel', {});
        }
        return this._finishedDeliveryPanel;
    },

    getInternalDeliveryPanel: function(cfg){
        if(!this._internalDeliveryPanel){
            this._internalDeliveryPanel = Ext._create('judicial.diligences.officer.InternalDeliveryPanel', {});
        }
        return this._internalDeliveryPanel;
    },
    
    refreshDiligenceGridOfPanel: function(panel) {
        panel.getDiligenceGrid().getStore().reload();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Minhas Diligências',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    {
                        xtype: 'tabpanel',
                        region: 'center',
                        activeTab: 0,
                        border: false,
                        items: [
                            this.getInDeliveryPanel(cfg),
                            this.getCancelDeliveryPanel(cfg),
                            this.getFinishedDeliveryPanel(cfg),
                            this.getInternalDeliveryPanel(cfg),
                        ]
                    }
                ]
            }
        );
        
        judicial.diligences.officer.DiligenceDashboard.superclass.constructor.call(this, cfg);
        
        this.getInDeliveryPanel().getDiligenceGrid().on({
            scope: this,
            afterAcceptDiligence: function(opts) {
                if (opts.withInternal) {
                    this.refreshDiligenceGridOfPanel(this.getInDeliveryPanel());
                    this.refreshDiligenceGridOfPanel(this.getInternalDeliveryPanel());
                }
            }
        });
        
        this.getInDeliveryPanel().getDeliveryGrid().on({
            scope: this,
            afterSignSuccess: function(entry) {
                if (entry.cancel_delivery) {
                    this.refreshDiligenceGridOfPanel(this.getInDeliveryPanel());
                    this.refreshDiligenceGridOfPanel(this.getCancelDeliveryPanel());
                } else if (entry.delivery_date) {
                    this.refreshDiligenceGridOfPanel(this.getInDeliveryPanel());
                    this.refreshDiligenceGridOfPanel(this.getFinishedDeliveryPanel());
                }
            }
        })
    }
});
