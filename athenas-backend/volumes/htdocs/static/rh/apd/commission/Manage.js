/**
 *
 **/
Ext._define('apd.commission.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getCommission: function() {
        if(!this.commission) {
            this.commission = Ext._create('apd.commission.CommissionGrid', {
                region: 'center',
            });

            this.commission.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(data.get('pk'));
                },
                rowdeselect: function() {
                    this.observe(null);
                }
            });
        }



        return this.commission;
    },

    getMemberCommissionGrid: function() {
        if(!this.membercommission) {
            this.membercommission = Ext._create('apd.membercommission.MemberCommissionGrid', {
                region: 'south',
                height: 400,
                title: 'Integrantes',
                disabled: true,
                gridAutoLoad: false,
            });

        }

        return this.membercommission;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeCommission();
        }

        return this._param;
    },

    observeCommission: function(){

        var value = this.observe();

        if(value) {
            this.getMemberCommissionGrid().enable();
            // this.getMemberCommissionGrid().member = value;
            this.getMemberCommissionGrid().setFilterProperty('commission', value);
            this.getMemberCommissionGrid().setParam('commission', value);
        }
        else {
            this.getMemberCommissionGrid().getStore().removeAll();
            this.getMemberCommissionGrid().disable();
        }
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Comissões'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getCommission(),
                    this.getMemberCommissionGrid(),
                ]
            }
        );

        apd.commission.Manage.superclass.constructor.call(this, cfg);
    }
});


/**
//  *
//  **/
// Ext._define('apd.commission.Manage', {
//     extend: 'toolkit.widget.TabPanel',

//     getCommissionGrid: function() {
//         if(!this.commission) {
//             this.commission = Ext._create('apd.membercommission.CommissionGrid', {
//                 region: 'center',
//                 title: 'Comissão',
//                 minHeight: 200,
//             });

            // this.commission.getSelectionModel().on({
            //     scope: this,
            //     rowselect: function(sm, index, data) {
            //         this.observe(data.get('pk'));
            //     },
            //     rowdeselect: function() {
            //         this.observe(null);
            //     }
            // });

//         }

//         return this.commission;
//     },

//     getMemberCommissionGrid: function() {
//         if(!this.membercommission) {
//             this.membercommission = Ext._create('apd.membercommission.MemberCommissionGrid', {
//                 region: 'south',
//                 height: 400,
//                 title: 'Integrantes',
//                 disabled: true,
//                 gridAutoLoad: false,
//             });

//         }

//         return this.membercommission;
//     },

//     observe: function(value, prevent) {
//         prevent = core.nullValue(prevent, false);

//         if(value !== undefined) {
//             this._param = value;

//             if(!prevent)
//                 this.observeCommission();
//         }

//         return this._param;
//     },

//     observeCommission: function(){

//         var value = this.observe();

//         if(value) {
//             this.getMemberCommissionGrid().enable();
//             // this.getMemberCommissionGrid().member = value;
//             this.getMemberCommissionGrid().setFilterProperty('commission', value);
//             this.getMemberCommissionGrid().setParam('commission', value);
//         }
//         else {
//             this.getMemberCommissionGrid().getStore().removeAll();
//             this.getMemberCommissionGrid().disable();
//         }
//     },

//     constructor: function(cfg) {
//         cfg = core.nullValue(cfg, {});

//         Ext.applyIf(
//             cfg,
//             {
//                 title: 'Gestor de Comissão'
//             }
//         );

//         Ext.apply(
//             cfg,
//             {
//                 layout: 'border',
//                 items: [
//                     this.getCommissionGrid(),
//                     this.getMemberCommissionGrid(),
//                 ]
//             }
//         );

//         apd.commission.Manage.superclass.constructor.call(this, cfg);
//     }
// });
