
Ext._define('judicial.dashboard.Sample', {
    extend: 'toolkit.widget.TabPanel',
    
    getMainContainer: function(cfg) {
        if(!this._mainContainer)
            this._mainContainer = Ext._create('Ext.Container', {
                autoEl: 'div',
                style: {
                    display: 'table',
                    minHeight: '10px',
                    margin: '25px auto'
                },
                items: [
                    Ext._create('judicial.dashboard.Panel', {
                        columns: 2,
                        cellHeight: 200,
                        panels: [
                            {
                                title: 'Acompanhamento de Procedimentos',
                                rest: 'judicial.OutCourtLawsuitRestful',
                                colspan: 2,
                                width: 900,
                                counters: [
                                    {
                                        title: 'Procedimentos de 2016',
                                        name: 'lawsuit_of_16',
                                        filter: [{property: 'year', value: 2016, stage: 1}],
                                        callback: {
                                            scope: this,
                                            fn: function() { console.log('empty'); }
                                        }
                                    },
                                    {
                                        title: 'Procedimentos de 2017',
                                        name: 'lawsuit_of_17',
                                        filter: [{property: 'year', value: 2017, stage: 1}],
                                        callback: {
                                            scope: this,
                                            fn: function() { console.log('empty'); }
                                        }
                                    },
                                    {
                                        title: 'Procedimentos de 2018',
                                        name: 'lawsuit_of_18',
                                        filter: [{property: 'year', value: 2018, stage: 1}],
                                        callback: {
                                            scope: this,
                                            fn: function() { console.log('empty'); }
                                        }
                                    },
                                    {
                                        title: 'Procedimentos de 2019',
                                        name: 'lawsuit_of_19',
                                        filter: [{property: 'year', value: 2019, stage: 1}],
                                        callback: {
                                            scope: this,
                                            fn: function() { console.log('empty'); }
                                        }
                                    }
                                ]
                            },
                            {
                                title: 'Acompanhamento de Diligências',
                                rest: 'judicial.OutCourtLawsuitRestful',
                                width: 446,
                                counters: []
                            },
                            {
                                title: 'Termos de Ajustamentos de Conduta',
                                rest: 'judicial.OutCourtLawsuitRestful',
                                width: 446,
                                counters: []
                            },
                            {
                                title: 'Recomendações',
                                rest: 'judicial.OutCourtLawsuitRestful',
                                width: 450,
                                counters: []
                            }
                        ]
                    })
                ]
            });
    
        return this._mainContainer;
    },
    
    constructor: function(cfg) {
        cfg = (cfg || {});
        
        Ext.applyIf(cfg, {
            title: 'Undefined title',
            items: [
                this.getMainContainer(cfg)
            ]
        });
        
        judicial.dashboard.Sample.superclass.constructor.call(this, cfg);
    }
});