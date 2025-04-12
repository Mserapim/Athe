rh.employee.specialized.tab.fields.Health = Ext.extend(
    rh.employee.specialized.tab.fields.Field,
    {
        constructor: function(cfg) {
            rh.employee.specialized.tab.fields.Health.superclass.constructor.call(this, cfg);
        },

        observerNaturalPersonPk: function(){
            rh.employee.specialized.tab.fields.Health.superclass.observerNaturalPersonPk.call(this, {});
            if(this.myParams('naturalPersonPk')){
                this.getSpecialNeedsField().objectId(this.myParams('naturalPersonPk'));
                this.getSeriousDiseasesField().objectId(this.myParams('naturalPersonPk'));

                this.getDeficiencyInformationGrid().enable();
                this.getDeficiencyInformationGrid().setParam('naturalperson', this.myParams('naturalPersonPk'));
                this.getDeficiencyInformationGrid().setFilterProperty('naturalperson__pk', this.myParams('naturalPersonPk'), 100);
            }else{
                this.getDeficiencyInformationGrid().setParam('naturalperson', undefined);
                this.getDeficiencyInformationGrid().removeFilterProperty('naturalperson__pk', 100, false);
                this.getDeficiencyInformationGrid().disable();

                this.getSpecialNeedsField().objectId(undefined);
                this.getSeriousDiseasesField().objectId(undefined);

                this.getSpecialNeedsField().disable();
                this.getSeriousDiseasesField().disable();
            }
        },

        fields: function(cfg){
            return [
                Ext._create('Ext.Panel', {
                    title: 'Necessidades especiais',
                    items: [
                        this.getSpecialNeedsField({}),
                    ]
                }),
                Ext._create('Ext.Panel', {
                    title: 'Doenças Graves',
                    items: [
                        this.getSeriousDiseasesField({}),
                    ]
                }),
                this.getDeficiencyInformationGrid({}),
            ];
        },

        getSpecialNeedsField: function(cfg) {
            if(!this._specialNeedsField)
                this._specialNeedsField = Ext._create('core.fields.RelatedRestfulField', {
                    region: 'north',
                    xtype: 'rest-relatedfield',
                    name: 'necessidades_especiais',
                    displayField: 'unicode',
                    allowBlank: false,
                    relatedname: 'pessoa',
                    rest: 'rh.person.naturalperson.Restful',
                    sourceRest: 'rh.necessidadeespecial.Restful',
                    width: '100%',
                    minHeight: 150,
                    height: 190,
                    border: false
                });

            return this._specialNeedsField;
        },

        getSeriousDiseasesField: function(cfg) {
            if(!this._seriousDiseasesField)
                this._seriousDiseasesField = Ext._create('core.fields.RelatedRestfulField', {
                    region: 'center',
                    xtype: 'rest-relatedfield',
                    name: 'serious_diseases',
                    displayField: 'name',
                    allowBlank: false,
                    relatedname: 'in_pessoafisica',
                    rest: 'rh.person.naturalperson.Restful',
                    sourceRest: 'rh.seriousdiseases.Restful',
                    width: '100%',
                    minHeight: 150,
                    height: 190,
                    border: false
                });

            return this._seriousDiseasesField;
        },

        getDeficiencyInformationGrid: function(cfg) {
            if(!this._deficiencyInformationGrid)
                this._deficiencyInformationGrid = Ext._create('rh.deficiencyinformation.Grid',{
                    title: 'Informações complementares de deficiência',
                    hideItemsToolbar: ['search', 'download'],
                    region: 'south',
                    border: false,
                    scope: this,
                    minHeight: 150,
                    height: 190,
                    columnAction: false,
                });
            return this._deficiencyInformationGrid;
        },
    }
);
