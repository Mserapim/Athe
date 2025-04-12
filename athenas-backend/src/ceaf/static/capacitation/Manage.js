/**
 *
 **/
Ext._define('ceaf.capacitation.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getCapacitation: function() {
        if(!this.capacitation) {
            this.capacitation = Ext._create('ceaf.capacitation.Grid', {
                title: 'Capacitações',
                region: 'center',
            });
        }

         this.capacitation.getSelectionModel().on({
            scope: this,
            'rowselect': function(sm, index, record) {
                this.setCapacitation(record.data.pk);
            },
            'rowdeselect': function(sm) {
                this.setCapacitation(null);
            }
        });

        this.capacitation.getStore().on({
            scope: this,
            'load': function() {
                this.setCapacitation(null);
            }
        });

        this.capacitation.getStore().on({
            scope: this,
            'load': function() {
                var selected = (this.capacitation.getSelectionModel().getSelected());

                if(selected)
                    this.setCapacitation(selected.get('pk'));
                else
                    this.setCapacitation(null);
            }
        });

        return this.capacitation;
    },

    setCapacitation: function(capacitationID) {
        this.capacitationID = capacitationID;
        this._observeCapacitation();
    },

    _observeCapacitation: function() {
        if(this.capacitationID) {
            this.getParticipants().enable();
            this.getParticipants().setFilterProperty('capacitation__id', this.capacitationID);
            this.getParticipants().setParam('capacitation', this.capacitationID);
            this.getParticipants().capacitation = this.capacitationID;
            
        }
        else {
            this.getParticipants().getStore().removeAll();
            this.getParticipants().disable();

        }
    },

    getParticipants: function() {
        if(!this.participants) {
            this.participants = Ext._create('ceaf.capacitation.participants.Grid', {
                title: 'Participantes',
                flex: 1.0,
                border: true,
            });
        }

        return this.participants;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Capacitações'
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getCapacitation(),
                    {
                        'listeners': {
                            scope: this,
                            'render': function() {
                            }
                        },
                        region: 'south',
                        layout: 'hbox',
                        minHeight: 150,
                        height: 400,
                        split: true,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getParticipants(),
                        ]
                    }
                ]
            }
        );

        ceaf.capacitation.Manage.superclass.constructor.call(this, cfg);
    }
});