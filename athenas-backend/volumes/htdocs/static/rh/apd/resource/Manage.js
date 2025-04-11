/**
 *
 **/
Ext._define('apd.resource.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getResource: function() {
        if(!this.resource) {
            this.resource = Ext._create('apd.resource.ResourceGrid', {
                region: 'center',
            });

            this.resource.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(data.get('evaluation'));
                },
                rowdeselect: function() {
                    this.observe(null);
                }
            });
        }

        return this.resource;
    },

    getScoreEvaluation: function() {
        if(!this.score) {
            this.score = Ext._create('apd.scoreevaluation.ScoreEvaluationGrid', {
                region: 'south',
                height: 400,
                title: 'Pontuação da Avaliação',
                disabled: true,
                // gridAutoLoad: false,
            });
        }

        return this.score;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeResource();
        }

        return this._param;
    },

    observeResource: function(){

        var value = this.observe();
        if(value) {
            this.getScoreEvaluation().enable();
            this.getScoreEvaluation().setFilterProperty('evaluation', value);
            this.getScoreEvaluation().setParam('evaluation', value);
        }
        else {
            this.getScoreEvaluation().getStore().removeAll();
            this.getScoreEvaluation().disable();
        }
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Recursos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getResource(),
                    this.getScoreEvaluation(),
                ]
            }
        );

        apd.resource.Manage.superclass.constructor.call(this, cfg);
    }
});
