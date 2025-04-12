Ext._define('corregedoria.cirdir.health.healtharea.IndicateEvaluator', {
    extend: 'Ext.Window',
    width: 800,

    modal: true,

    getEvaluatorGrid: function(cfg) {
        if(!this._evaluatorGrid) {
            this._evaluatorGrid = Ext._create('corregedoria.cirdir.evaluator.Grid', {
                region: 'center',
                height: 600,
            });
        }
        return this._evaluatorGrid;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            title: 'Cadastro de Avaliadores',
            items: [
              this.getEvaluatorGrid(cfg)
            ],
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ]
        });
        corregedoria.cirdir.health.healtharea.IndicateEvaluator.superclass.constructor.call(this, cfg);
    }

});
