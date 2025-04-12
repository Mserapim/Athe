/**
 *
 **/
Ext._define('rh.gfp.payroll.BankingConvenantManage', {
    extend: 'toolkit.widget.TabPanel',

    getBankingConvenantGrid: function() {
        if(!this._bankingConvenantGrid) {
            this._bankingConvenantGrid = Ext._create('rh.gfp.payroll.BankingConvenantGrid', {
                region: 'center',
                gridAutoLoad: true
            });

            // this._bankingConvenantGrid.setFilterProperty('active', true, 100002, false);
            // this._bankingConvenantGrid.setFilterProperty('removed_by', null, 3000);
        }

        return this._bankingConvenantGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Convênios Bancários'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getBankingConvenantGrid(),
                ]
            }
        );

        rh.gfp.payroll.BankingConvenantManage.superclass.constructor.call(this, cfg);
    }
});
