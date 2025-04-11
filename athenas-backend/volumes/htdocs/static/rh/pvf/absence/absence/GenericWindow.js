Ext._define('rh.pvf.absence.absence.GenericWindow', {
  extend: 'rh.pvf.portalrequestusufruct.Window',

  rest: 'rh.pvf.absence.absence.Restful',

  height:500,

  getFormItems: function (cfg) {
    return [];
  },

  
  getFormPanel: function (cfg) {
    if (!this._formPanel)
        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            items: this.getTabPanel(cfg),
            submit_all_checks: true
        });

    return this._formPanel;
},

  // getFormPanel: function (cfg) {
  //   if (!this._formPanel)
  //     this._formPanel = Ext._create('Ext.form.FormPanel', {
  //       frame: true,
  //       border: false,
  //       labelWidth: 100,
  //       items: this.getFormItems(cfg)
  //     });
  //   return this._formPanel;
  // },

  getTabPanel: function (cfg) {
    if (!this._tabPanel)
        this._tabPanel = Ext._create('Ext.TabPanel', {
            height: 900,
            border: false,
            activeTab: 0,
            deferredRender: false,
            items: [
                cfg.action == "create"?
                [this.getManagerPanel(cfg),this.getSubstitutePanel(cfg)]:
                [this.getManagerPanel(cfg),this.getSubstitutePanel(cfg)]
            ]
        });

    return this._tabPanel;
 },

  getManagerPanel: function (cfg) {
    if (!this._managementPanel)
        this._managementPanel = Ext._create('Ext.Panel', {
            frame: true,
            border: false,
            title: 'Principal',
            layout: 'form',
            items: [
              this.getFormItems(cfg)
            ]
          });    

    return this._managementPanel;
  },

  addSubstitute:function(cfg,params){
    var row = new  this._recordSubstituteField({
        start_date:params.start_date ,
        end_date: params.end_date,
        substitute_id: params.substitute_id,
        exercise_id:params.exercise_id,
        substitute:this.getSubstitute()._comboField.lastSelectionText,
        exercise:this.getExercise()._comboField.lastSelectionText,
    });
    this.getSubstituteStore().add(row);
    this.getStartDate().setValue(null)
    this.getFinalDate().setValue(null)
    if (!cfg.params.exercise_one)
      this.getExercise().setValue(null)
    this.getSubstitute().setValue(null)
  },

});

