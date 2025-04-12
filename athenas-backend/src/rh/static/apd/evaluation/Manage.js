/**
 *
 **/
Ext._define('apd.evaluation.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getAPD: function() {
        if(!this.apd) {
            this.apd = Ext._create('apd.evaluation.EvaluationGrid', {
                region: 'center',
            });

            this.apd.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    console.log(record.data);
                    if(record.data.can_boss_evaluate && (record.data.deadline == 1 || record.data.deadline ==2) )
                        this.apd.setActionEvaluationEnable();
                    else
                        this.apd.setActionEvaluationDisable();
                },
            });
        }

        return this.apd;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Avaliação APD'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getAPD(),
                ]
            }
        );

        apd.evaluation.Manage.superclass.constructor.call(this, cfg);
    }
});
